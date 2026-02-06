from adapters.sqlalchemy.models import (
    Account as SQLAlchemyAccount,
    PaymentEntry as SQLAlchemyPaymentEntry,
)
from domain.models import (
    Money,
    AccountId,
    PaymentEntryId,
    TransactionId,
    UserId,
    Account,
    PaymentEntry,
)


class PaymentEntryMapper:

    @staticmethod
    def to_domain(orm_model: SQLAlchemyPaymentEntry) -> PaymentEntry:
        domain_model = PaymentEntry(
            id_=PaymentEntryId(orm_model.id),
            transaction_id=TransactionId(orm_model.transaction_id),
            account_id=AccountId(orm_model.account_id),
            amount=Money(orm_model.amount),
            is_accrued=orm_model.is_accrued,
        )

        return domain_model

    @staticmethod
    def to_orm(domain_model: PaymentEntry) -> SQLAlchemyPaymentEntry:
        orm_model = SQLAlchemyPaymentEntry(
            id=domain_model.id_,
            transaction_id=domain_model.transaction_id,
            account_id=domain_model.account_id,
            amount=domain_model.amount,
            is_accrued=domain_model.is_accrued,
        )

        return orm_model


class AccountMapper:

    @staticmethod
    def to_domain(orm_model: SQLAlchemyAccount) -> Account:
        domain_model = Account(
            id_=AccountId(orm_model.id),
            user_id=UserId(orm_model.user_id),
            balance=Money(orm_model.balance),
            payments={
                PaymentEntryMapper.to_domain(entry) for entry in orm_model.payments
            },
        )

        return domain_model

    @staticmethod
    def to_orm(domain_model: Account) -> SQLAlchemyAccount:
        orm_model = SQLAlchemyAccount(
            id=domain_model.id_,
            user_id=domain_model.user_id,
            balance=domain_model.balance,
            payments=[
                PaymentEntryMapper.to_orm(entry) for entry in domain_model.payments
            ],
        )

        return orm_model
