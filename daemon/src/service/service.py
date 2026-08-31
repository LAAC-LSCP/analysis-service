import asyncio
import threading
from datetime import datetime, timedelta, timezone
from typing import Type

from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import RunTask
from analysis_service_core.src.redis.commands import (
    Command,
    CompleteTask,
    FailTask,
    ReportProgress,
)
from analysis_service_core.src.redis.pubsub import PubSub
from analysis_service_core.src.redis.queue import Queue
from tenacity import Retrying, stop_after_attempt, wait_fixed

from src.core.elsi_api import Task, Tasks
from src.core.types import TaskStatus
from src.service.command_handlers import CommandHandlers
from src.service.http_client import HTTPClient

logger = LoggerFactory.get_logger(__name__)


class Service:
    S_PER_UPDATE: int = 10
    S_PER_QUEUE_FETCH: int = 1

    # A task stuck at RUNNING with no update for longer than this is considered
    # stalled (crashed, killed, or otherwise never going to report back) and is
    # marked FAILED. Proportional to the duration of the recording(s) it covers
    # when ELSI reports that; otherwise this floor alone is used.
    STALE_TASK_FLOOR_S: float = 600.0
    STALE_TASK_DURATION_FACTOR: float = 1 / 60

    _completion_queue: Queue
    _fail_queue: Queue
    _progress_bus: PubSub
    _command_handlers: CommandHandlers
    _http_client: HTTPClient
    _stop_event: threading.Event

    def __init__(
        self,
        completion_queue: Queue,
        progress_bus: PubSub,
        command_handlers: CommandHandlers,
        http_client: HTTPClient,
        fail_queue: Queue,
    ):
        self._completion_queue = completion_queue
        self._fail_queue = fail_queue
        self._progress_bus = progress_bus
        self._command_handlers = command_handlers
        self._http_client = http_client
        self._stop_event = threading.Event()

    async def start(self) -> None:
        logger.info("Daemon started")
        loop = asyncio.get_event_loop()
        redis_task = loop.run_in_executor(None, self._listen_and_handle_completion)
        progress_task = loop.run_in_executor(None, self._listen_and_handle_progress)
        api_task = self._external_api_loop()

        await asyncio.gather(redis_task, progress_task, api_task)
        logger.info("Daemon stopped")

    def stop(self) -> None:
        """Signal all loops to stop after their current iteration."""
        logger.info("Stop requested; shutting down gracefully...")
        self._stop_event.set()

    async def _external_api_loop(self) -> None:
        while not self._stop_event.is_set():
            current_t = datetime.now()

            logger.info("Loading new tasks...")
            self.tick()

            sleep_t: float = (
                current_t + timedelta(seconds=self.S_PER_UPDATE) - datetime.now()
            ).total_seconds()

            await self._interruptible_sleep(sleep_t if sleep_t > 0 else 0)

    async def _interruptible_sleep(self, duration_s: float) -> None:
        """Sleep in small chunks so stop() takes effect promptly, not after the
        full interval."""
        remaining = duration_s
        while remaining > 0 and not self._stop_event.is_set():
            step = min(self.S_PER_QUEUE_FETCH, remaining)
            await asyncio.sleep(step)
            remaining -= step

    def tick(self) -> None:
        try:
            logger.info("Requesting all tasks through external API...")
            all_tasks = self._http_client.get_all_tasks()
        except Exception as e:
            logger.error(f"Failed to fetch tasks: {e}")

            return

        new_tasks = {
            task for task in all_tasks if task.status_label == TaskStatus.PENDING
        }

        if len(new_tasks) != 0:
            logger.info(f"Received new tasks: {new_tasks}")

        for task in new_tasks:
            try:
                message: RunTask = RunTask(
                    task_id=task.task_uid,
                    dataset_uid_label=task.dataset_uid_label,
                    operation=task.model_name,
                    resume=False,
                )

                logger.info(f"Publishing task with id '{task.task_uid}' to redis")
                self._invoke_handlers(RunTask, message)
            except Exception:
                logger.exception(f"Failed to dispatch new task '{task}'.")

        self._fail_stale_running_tasks(all_tasks)

    def _fail_stale_running_tasks(self, all_tasks: Tasks) -> None:
        running_tasks = {
            task for task in all_tasks if task.status_label == TaskStatus.RUNNING
        }

        for task in running_tasks:
            try:
                self._fail_if_stale(task)
            except Exception:
                logger.exception(f"Failed to check staleness for task '{task}'.")

    def _fail_if_stale(self, task: Task) -> None:
        budget_s = self.STALE_TASK_FLOOR_S
        if task.duration_seconds is not None:
            budget_s = max(
                budget_s, task.duration_seconds * self.STALE_TASK_DURATION_FACTOR
            )

        age_s = (datetime.now(timezone.utc) - task.modified).total_seconds()
        if age_s <= budget_s:
            return

        logger.warning(
            f"Task '{task.task_uid}' has been RUNNING with no update for "
            f"{age_s:.0f}s (budget: {budget_s:.0f}s). Marking as failed."
        )

        self._invoke_handlers(
            FailTask,
            FailTask(
                task_id=task.task_uid,
                reason=f"No update received for {age_s:.0f}s "
                f"(budget: {budget_s:.0f}s); assumed stalled or crashed.",
            ),
        )

    def _listen_and_handle_completion(self) -> None:
        while not self._stop_event.is_set():
            completion_message = self._completion_queue.dequeue()
            if completion_message:
                self._handle_message(completion_message, CompleteTask)

            fail_message = self._fail_queue.dequeue()
            if fail_message:
                self._handle_message(fail_message, FailTask)

            if not completion_message and not fail_message:
                # Bounded, interruptible wait: avoids a busy loop while idle, and
                # lets stop() take effect promptly instead of spinning forever.
                self._stop_event.wait(timeout=self.S_PER_QUEUE_FETCH)

    def _listen_and_handle_progress(self) -> None:
        while not self._stop_event.is_set():
            # get_message(timeout=...) polls with a bound, unlike listen() which
            # blocks on the socket indefinitely and can't observe stop().
            message = self._progress_bus.get_message(timeout=self.S_PER_QUEUE_FETCH)
            if not message:
                continue

            self._handle_message(message["data"], ReportProgress)

    def get_completion_message_and_handle(
        self, max_attempts: int = 3, wait_seconds: float = 0.1
    ) -> None:
        """
        Looks for next message, mostly for testing purposes
        """
        self._get_message_and_handle(
            self._completion_queue, CompleteTask, max_attempts, wait_seconds
        )

    def get_fail_message_and_handle(
        self, max_attempts: int = 3, wait_seconds: float = 0.1
    ) -> None:
        """
        Looks for next fail message, mostly for testing purposes
        """
        self._get_message_and_handle(
            self._fail_queue, FailTask, max_attempts, wait_seconds
        )

    def get_progress_message_and_handle(
        self, max_attempts: int = 3, wait_seconds: float = 0.1
    ) -> None:
        """
        Looks for next progress message, mostly for testing purposes
        """
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait_seconds),
            reraise=True,
        ):
            with attempt:
                message = self._progress_bus.get_message()

                if message:
                    self._handle_message(message["data"], ReportProgress)

                    return
                else:
                    raise Exception("Retrying...")

        return

    def _get_message_and_handle(
        self,
        queue: Queue,
        command_cls: Type[Command],
        max_attempts: int,
        wait_seconds: float,
    ) -> None:
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait_seconds),
            reraise=True,
        ):
            with attempt:
                command_dict = queue.dequeue()

                if command_dict:
                    self._handle_message(command_dict, command_cls)

                    return
                else:
                    raise Exception("Retrying...")

        return

    def _handle_message(self, command_dict: dict, command_cls: Type[Command]) -> None:
        logger.info(f"Handling message: {command_dict}")
        command = command_cls.from_dict(command_dict)

        self._invoke_handlers(command_cls, command)

    def _invoke_handlers(self, command_cls: Type[Command], command: Command) -> None:
        for handler in self._command_handlers.get(command_cls, []):
            try:
                handler(command)
            except Exception:
                logger.exception(
                    f"Handler failed for {command_cls.__name__} command: {command}"
                )
