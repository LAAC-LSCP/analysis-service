import asyncio
from datetime import datetime, timedelta
from time import sleep

from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import RunTask
from analysis_service_core.src.redis.commands import CompleteTask
from analysis_service_core.src.redis.queue import Queue
from tenacity import Retrying, stop_after_attempt, wait_fixed

from src.core.types import TaskStatus
from src.service.command_handlers import CommandHandlers
from src.service.http_client import HTTPClient

logger = LoggerFactory.get_logger(__name__)


class Service:
    S_PER_UPDATE: int = 10
    S_PER_QUEUE_FETCH: int = 1

    _completion_queue: Queue
    _command_handlers: CommandHandlers
    _http_client: HTTPClient

    def __init__(
        self,
        completion_queue: Queue,
        command_handlers: CommandHandlers,
        http_client: HTTPClient,
    ):
        self._completion_queue = completion_queue
        self._command_handlers = command_handlers
        self._http_client = http_client

    async def start(self) -> None:
        logger.info("Daemon started")
        loop = asyncio.get_event_loop()
        redis_task = loop.run_in_executor(None, self._listen_and_handle_redis)
        api_task = self._external_api_loop()

        await asyncio.gather(redis_task, api_task)

    async def _external_api_loop(self) -> None:
        while True:
            current_t = datetime.now()

            logger.info("Loading new tasks...")
            self.tick()

            sleep_t: float = (
                current_t + timedelta(seconds=self.S_PER_UPDATE) - datetime.now()
            ).total_seconds()

            await asyncio.sleep(sleep_t if sleep_t > 0 else 0)

    def tick(self) -> None:
        try:
            logger.info("Requesting all tasks through external API...")
            all_tasks = self._http_client.get_all_tasks()
        except Exception as e:
            logger.err(f"Failed to fetch tasks: {e}")

            return

        new_tasks = {
            task for task in all_tasks if task.status_label == TaskStatus.PENDING
        }

        if len(new_tasks) != 0:
            logger.info(f"Received new tasks: {new_tasks}")

        for task in new_tasks:
            message: RunTask = RunTask(
                task_id=task.task_uid,
                dataset_uid_label=task.dataset_uid_label,
                operation=task.model_name,
            )

            logger.info(f"Publishing task with id '{task.task_uid}' to redis")
            for handler in self._command_handlers.get(RunTask, []):
                handler(message)

    def _listen_and_handle_redis(self) -> None:
        while True:
            # Why not pubsub? Because if the Daemon is down things get lost
            message = self._completion_queue.dequeue()
            if message:
                self._handle_completion(message)
            sleep(self.S_PER_QUEUE_FETCH)

    def get_completion_message_and_handle(
        self, max_attempts: int = 3, wait_seconds: float = 0.1
    ) -> None:
        """
        Looks for next message, mostly for testing purposes
        """
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait_seconds),
            reraise=True,
        ):
            with attempt:
                command_dict = self._completion_queue.dequeue()

                if command_dict:
                    self._handle_completion(command_dict)

                    return
                else:
                    raise Exception("Retrying...")

        return

    def _handle_completion(self, command_dict: dict) -> None:
        logger.info(f"Handling message: {command_dict}")
        command = CompleteTask.from_dict(command_dict)

        for handler in self._command_handlers.get(CompleteTask, []):
            handler(command)
