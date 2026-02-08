from dtos import UserDTO
from domain.models import Account, PaymentEntry, UserId
from adapters.repository import AbstractAccountRepository


def get_user_accounts(
    user_id: UserId, account_repository: AbstractAccountRepository
) -> list[Account]:
    user_accounts = account_repository.get_user_accounts(user_id)
    return user_accounts


def get_user_payments(
    user_id: UserId, account_repository: AbstractAccountRepository
) -> list[PaymentEntry]:
    user_payments = account_repository.get_user_payments(user_id)
    return user_payments


def get_user_data(user_id: UserId) -> UserDTO:
    # TODO:
    raise NotImplementedError


def get_users():
    # TODO:
    raise NotImplementedError
