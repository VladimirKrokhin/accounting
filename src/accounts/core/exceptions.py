# User's Exceptions


class UserError(Exception):
    pass


class UserIsAlreadyExistsError(UserError):
    pass


class UserDoesNotExists(UserError):
    pass


# Exceptions during handling Payment System's transactions (via webhooks)


class PaymentSystemError(Exception):
    pass


class SignatureIsNotValid(PaymentSystemError):
    pass


# Payment Entry's Exceptions


class PaymentEntryError(Exception):
    pass


class PaymentEntryIsNotUniqueError(PaymentEntryError):
    pass


class PaymentEntryDoesNotExistsError(PaymentEntryError):
    pass


class PaymentEntryAlreadyAccrued(PaymentEntryError):
    pass


# Account's Exceptions


class AccountError(Exception):
    pass


class AccountDoesNotExists(AccountError):
    pass
