from services.payment_system import process_payment_system_transaction
from domain.messages import (
    CreateUser,
    DeleteUser,
    HandlePaymentSystemTransaction,
    UpdateUser,
)
from services.user import create_user, delete_user, update_user

handlers = {
    HandlePaymentSystemTransaction: process_payment_system_transaction,
    CreateUser: create_user,
    UpdateUser: update_user,
    DeleteUser: delete_user,
}
