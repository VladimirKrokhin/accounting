# Исключения аутентификации и авторизации


class AuthError(Exception):
    pass


class AuthentificationError(AuthError):
    pass


class ExpiredSignatureError(AuthentificationError):
    pass


class InvalidTokenError(AuthentificationError):
    pass


class AuthorizationError(AuthError):
    pass


# Исключения при работе с пользователем


class UserError(Exception):
    pass


class UserIsAlreadyExistsError(UserError):
    pass


class UserDoesNotExists(UserError):
    pass


# Исключения при обработке транзакции от платежной системы


class PaymentSystemError(Exception):
    pass


class SignatureIsNotValid(PaymentSystemError):
    pass


# Исключения при работе с платежами


class PaymentEntryError(Exception):
    """Базовый класс для исключений и ошибок, связанных с платежом."""

    pass


class PaymentEntryIsNotUniqueError(PaymentEntryError):
    """Платеж дублируется."""

    pass


class PaymentEntryDoesNotExistsError(PaymentEntryError):
    """Платеж не найден."""

    pass


class PaymentEntryAlreadyAccrued(PaymentEntryError):
    """Платеж уже начислен."""

    pass
