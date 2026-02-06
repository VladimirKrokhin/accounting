from enum import Enum, auto
from services.account import (
    get_user_accounts,
    get_user_transactions,
    get_users_list_with_accounts,
)
from services.payment_system import process_payment_system_transaction
from domain.messages import HandlePaymentSystemTransaction


handlers = {
    #     None; get_user_accounts,
    #     None: get_user_transactions,
    #     None: get_users_list_with_accounts,
    HandlePaymentSystemTransaction: process_payment_system_transaction,
}
