import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from accounts.domain.messages import Message
    import accounts.service_layer.unit_of_work as unit_of_work


logger = logging.getLogger(__name__)

__all__ = ["MessageBus"]


class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        message_handlers: dict[type[Message], callable],
    ) -> None:
        self.uow = uow
        self.message_handlers = message_handlers

    def handle(self, message: Message) -> None:
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            self.handle_message(message)

    def handle_message(self, message: Message) -> None:
        handler = self.message_handlers[type(message)]

        try:
            logger.debug(f"handling message {message} with handler {handler}")
            handler(message)
        except Exception:
            logger.exception(f"Exception handling message {message}")
            raise
