from services.payment_system import process_payment_system_transaction
from domain.messages import HandlePaymentSystemTransaction


handlers = {
    HandlePaymentSystemTransaction: process_payment_system_transaction,
}
