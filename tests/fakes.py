from accounts.adapters.repository import (
    AbstractAccountRepository,
    AbstractUserRepository,
)
from accounts.core.entities import Account, PaymentEntry
from accounts.core.exceptions import AccountDoesNotExists, UserDoesNotExists
from accounts.core.types import AccountId, TransactionId, UserId
from accounts.dtos import UserDTO
from accounts.service_layer.unit_of_work import AbstractUnitOfWork


class FakeAccountRepository(AbstractAccountRepository):
    """Fake Accounts Repository."""

    def __init__(self, *accounts: Account) -> None:

        storage: dict[AccountId, Account] = {}
        account_serial: AccountId = AccountId(0)

        accs_with_id = [acc for acc in accounts if acc.id_ is not None]
        accs_without_id = [acc for acc in accounts if acc.id_ is None]

        for acc in accs_with_id:
            storage[acc.id_] = acc
            account_serial = max(account_serial, acc.id_)

        for acc in accs_without_id:
            account_serial += 1
            acc.id_ = account_serial
            storage[acc.id_] = acc

        self.storage: dict[AccountId, Account] = storage
        self.account_serial: int = account_serial

    async def does_payment_entry_exist_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        for account in self.storage.values():
            for entry in account.payments:
                if entry.transaction_id == transaction_id:
                    return True

        return False

    async def does_user_have_account(self, user_id: UserId, account_id: AccountId):
        for account in self.storage.values():
            if account.id_ == account_id and account.user_id == user_id:
                return True

        return False

    async def save_account(self, account: Account) -> AccountId:
        if account.id_ is None:
            self.account_serial += 1
            account.id_ = AccountId(self.account_serial)
            for entry in account.payments:
                entry.account_id = account.id_
        elif not await self.does_account_exist(account.id_):
            self.account_serial = account.id_ + 1

        self.storage[account.id_] = account

        return account.id_

    async def does_account_exist(self, account_id: AccountId) -> bool:
        return account_id in self.storage

    async def get_account_by_id(self, account_id: AccountId) -> Account:
        if not await self.does_account_exist(account_id):
            raise AccountDoesNotExists(f"Account with id={account_id} does not exists")

        return self.storage[account_id]

    async def get_user_accounts(self, user_id: UserId) -> list[Account]:
        user_accounts = []

        for account in self.storage.values():
            if account.user_id == user_id:
                user_accounts.append(account)

        return user_accounts

    async def get_user_payments(self, user_id: UserId) -> list[PaymentEntry]:
        user_accounts = await self.get_user_accounts(user_id)
        user_payments = []

        for account in user_accounts:
            user_payments.extend(account.payments)

        return user_payments


class FakeUserRepository(AbstractUserRepository):
    """Fake User Repository."""

    def __init__(self, *users: UserDTO) -> None:
        storage: dict[UserId, UserDTO] = {}
        user_serial: UserId = UserId(0)

        users_with_id = [user for user in users if user.user_id is not None]
        users_without_id = [user for user in users if user.user_id is None]

        for user in users_with_id:
            storage[user.user_id] = user
            user_serial = max(user_serial, user.user_id)

        for user in users_without_id:
            user_serial += 1
            user.user_id = user_serial
            storage[user.user_id] = user

        self.storage: dict[UserId, UserDTO] = storage
        self.user_serial: int = user_serial

    async def does_user_exist(self, user_id: UserId) -> bool:
        for user in self.storage.values():
            if user.user_id == user_id:
                return True

        return False

    async def does_user_exist_by_email(self, email: str) -> bool:
        for user in self.storage.values():
            if user.email == email:
                return True

        return False

    async def get_user(self, user_id: UserId) -> UserDTO:
        if not await self.does_user_exist(user_id):
            raise UserDoesNotExists(f"Cannot get User {user_id}: not found")

        user = self.storage[user_id]
        return user

    async def save_user(self, user: UserDTO) -> UserId:
        if user.user_id is None:
            self.user_serial += 1
            user.user_id = UserId(self.user_serial)

        elif user.user_id not in self.storage:
            if isinstance(user.user_id, int) and user.user_id > self.user_serial:
                self.user_serial = user.user_id

        self.storage[user.user_id] = user

        return user.user_id

    async def delete_user(self, user_id: UserId) -> None:
        if not await self.does_user_exist(user_id):
            raise UserDoesNotExists(f"Cannot delete: User {user_id} not found")

        self.storage.pop(user_id)

    async def get_users(self) -> list[UserDTO]:
        users = list(self.storage.values())
        return users

    async def get_users_by_email(self, email: str) -> list[UserDTO]:
        users = []
        for user in self.storage.values():
            if user.email == email:
                users.append(user)

        return users


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        accounts: FakeAccountRepository | None = None,
        users: FakeUserRepository | None = None,
    ):
        if accounts is None:
            accounts = FakeAccountRepository()

        if users is None:
            users = FakeUserRepository()

        self.accounts = accounts
        self.users = users
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def rollback(self):
        pass
