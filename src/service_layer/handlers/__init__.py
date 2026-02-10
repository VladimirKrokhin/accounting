from domain.messages import (
    CreateUser,
    DeleteUser,
    HandlePaymentSystemTransaction,
    UpdateUser,
)

from service_layer.handlers.payment_system import process_payment_system_transaction
from service_layer.handlers.user import create_user, delete_user, update_user

message_handlers = {
    # Обработка веб-хуков от платежной системы
    HandlePaymentSystemTransaction: process_payment_system_transaction,
    # Операции над пользователем
    CreateUser: create_user,
    UpdateUser: update_user,
    DeleteUser: delete_user,
}
