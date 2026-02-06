import inspect
from typing import Callable

from adapters.repository import AbstractAccountRepository
from services import handlers
from domain.messages import Message


def bootstrap(
    account_repository: AbstractAccountRepository,
    secret: str,
) -> dict[type[Message], Callable]:

    dependencies = {"account_repository": account_repository, "secret": secret}

    injected_handlers = {
        message: inject_dependencies(handler, dependencies)
        for message, handler in handlers.items()
    }

    return injected_handlers


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)
