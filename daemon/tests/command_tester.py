from typing import List, Type, TypedDict

import analysis_service_core.src.redis.commands as commands

from src.service.command_handlers import CommandHandler, CommandHandlers


class Call(TypedDict):
    type: Type[commands.Command]
    message: commands.Command
    handler_name: str
    threw_error: bool


class CommandTester:
    """
    Generic spy class for commands

    Wraps commands in such a way that it records information about
    command calls, e.g., name of handler or whether an error was thrown
    """

    _calls: List[Call]
    _command_handlers: CommandHandlers

    def __init__(self, command_handlers: CommandHandlers):
        self._calls = []
        self._command_handlers = {
            command: [
                self._track_command_handler(command, handler) for handler in handlers
            ]
            for command, handlers in command_handlers.items()
        }

    def _track_command_handler(
        self, command_cls: Type[commands.Command], handler: CommandHandler
    ) -> CommandHandler:
        def _call_command(command: commands.Command) -> None:
            threw_error = False

            try:
                handler(command)
            except Exception:
                threw_error = True
            finally:
                call = Call(
                    type=command_cls,
                    message=command,
                    handler_name=str(handler.__name__),  # type: ignore
                    threw_error=threw_error,
                )
                self._calls.append(call)

        return _call_command

    @property
    def command_handlers(self) -> CommandHandlers:
        return self._command_handlers

    @property
    def calls(self) -> List[Call]:
        return self._calls
