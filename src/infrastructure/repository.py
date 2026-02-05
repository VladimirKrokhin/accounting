from domain import Account, AccountId, UserId, PaymentEntry, TransactionId


class FakeAccountRepository:
    def __init__(
        self,
        storage: dict[AccountId, Account] | None = None,
        account_serial: AccountId = AccountId(0),
    ) -> None:

        if storage is None:
            storage = {}

        self.storage: dict[AccountId, Account] = storage
        self.account_serial: int = account_serial

    def is_payment_entry_exists_by_transaction_id(
        self, transaction_id: TransactionId
    ) -> bool:
        for account in self.storage.values():
            for entry in account.payments:
                if entry.transaction_id == transaction_id:
                    return True

        return False

    def is_user_has_account(self, user_id: UserId, account_id: AccountId):
        for account in self.storage.values():
            if account.id_ == account_id and account.user_id == user_id:
                return True

        return False

    def save_account(self, account: Account) -> AccountId:
        if not self.is_account_exists(account):
            self.account_serial += 1
            account.id_ = self.account_serial
            for entry in account.payments:
                entry.account_id = account.id_

        self.storage[account.id_] = account

        return account.id_

    def is_account_exists(self, account_id: AccountId) -> bool:
        return account_id in self.storage

    def get_account_by_id(self, account_id: AccountId) -> Account:
        if not self.is_account_exists(account_id):
            raise ValueError("Указанный счет не существует")

        return self.storage[account_id]
