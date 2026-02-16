from accounts.dtos import UserDTO, UserType
from accounts.domain.types import (
    Money,
    AccountId,
    PaymentEntryId,
    TransactionId,
    UserId,
)
from accounts.domain.models import (
    Account,
    PaymentEntry,
)
from accounts.adapters.sqlalchemy.models import (
    Account as SQLAlchemyAccount,
    AccountsUser,
    Administrator,
    PaymentEntry as SQLAlchemyPaymentEntry,
    User,
)

__all__ = ["PaymentEntryMapper", "AccountMapper", "UserMapper"]


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


class UserMapper:
    @staticmethod
    def to_dto(orm_user: User) -> UserDTO:
        return UserDTO(
            user_id=UserId(orm_user.id),
            email=orm_user.email_address,
            full_name=orm_user.full_name or "",
            user_type=UserType(orm_user.type),
            password_hash=orm_user.password_hash,
        )

    @staticmethod
    def to_orm(user_dto: UserDTO) -> User:
        model_map = {
            "user": AccountsUser,
            "admin": Administrator,
        }

        model_class = model_map.get(user_dto.user_type, User)

        match user_dto.user_type:
            case UserType.USER:
                model_class = AccountsUser(
                    id=user_dto.user_id,
                    full_name=user_dto.full_name,
                    email_address=user_dto.email,
                    password_hash=user_dto.password_hash,
                )
            case UserType.ADMIN:
                model_class = Administrator(
                    id=user_dto.user_id,
                    full_name=user_dto.full_name,
                    email_address=user_dto.email,
                    password_hash=user_dto.password_hash,
                )
            case _:
                raise ValueError

        return model_class
