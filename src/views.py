from dtos import UserDTO
from domain.models import Account, PaymentEntry, UserId
from domain.exceptions import UserDoesNotExists
from adapters.repository import (
    AbstractAccountRepository,
    AbstractUserRepository,
)


def get_user_accounts(
    user_id: UserId,
    account_repository: AbstractAccountRepository,
    user_repository: AbstractUserRepository,
) -> list[Account]:
    is_user_exists = user_repository.is_user_exists(user_id)

    if not is_user_exists:
        raise UserDoesNotExists

    user_accounts = account_repository.get_user_accounts(user_id)
    return user_accounts


def get_user_payments(
    user_id: UserId,
    account_repository: AbstractAccountRepository,
    user_repository: AbstractUserRepository,
) -> list[PaymentEntry]:
    is_user_exists = user_repository.is_user_exists(user_id)

    if not is_user_exists:
        raise UserDoesNotExists

    user_payments = account_repository.get_user_payments(user_id)
    return user_payments


def get_user_data(user_id: UserId, user_repository: AbstractUserRepository) -> UserDTO:
    user = user_repository.get_user(user_id)
    return user


def get_users(user_repository: AbstractUserRepository):
    users = user_repository.get_users()
    return users
