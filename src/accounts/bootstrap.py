import inspect

from accounts.service_layer import unit_of_work
from accounts.service_layer.handlers import message_handlers
from accounts.service_layer.message_bus import MessageBus

__all__ = ["bootstrap"]


def bootstrap(
    uow: unit_of_work.AbstractUnitOfWork,
) -> MessageBus:

    dependencies = {
        "uow": uow,
    }

    injected_handlers = {
        message: inject_dependencies(handler, dependencies)
        for message, handler in message_handlers.items()
    }

    mb = MessageBus(message_handlers=injected_handlers, uow=uow)

    return mb


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)
