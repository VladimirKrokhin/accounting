from accounts.dtos import UserDTO
from accounts.core.entities import Account, PaymentEntry, UserId
from accounts.core.exceptions import UserDoesNotExists
from accounts.service_layer.unit_of_work import AbstractUnitOfWork


async def get_user_accounts(
    user_id: UserId,
    uow: AbstractUnitOfWork,
) -> list[Account]:

    with uow:
        account_repository = uow.accounts
        user_repository = uow.users
        is_user_exists = await user_repository.does_user_exist(user_id)

        if not is_user_exists:
            raise UserDoesNotExists

        user_accounts = await account_repository.get_user_accounts(user_id)
    return user_accounts


async def get_user_payments(
    user_id: UserId,
    uow: AbstractUnitOfWork,
) -> list[PaymentEntry]:

    with uow:
        account_repository = uow.accounts
        user_repository = uow.users
        is_user_exists = await user_repository.does_user_exist(user_id)

        if not is_user_exists:
            raise UserDoesNotExists

        user_payments = await account_repository.get_user_payments(user_id)

    return user_payments


async def get_user_data(user_id: UserId, uow: AbstractUnitOfWork) -> UserDTO:
    with uow:
        user_repository = uow.users

        user = await user_repository.get_user(user_id)

    return user


async def get_users(uow: AbstractUnitOfWork):
    with uow:
        user_repository = uow.users

        users = await user_repository.get_users()

    return users
