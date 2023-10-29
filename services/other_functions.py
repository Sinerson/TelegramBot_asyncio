from icecream import ic
from db.fake_marketing_actions import PRISE_ACTION

from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, getClientCodeByContractCode, \
    get_phonenumber_by_user_id_query, getContractCode
from db.sybase import DbConnection


# Получаем из хэндлера callback data и выделяем из нее код контракта, после чего отдаем его назад
def contract_code_from_callback(callback_data):
    for word in callback_data.split():
        normalized_contract_code = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_contract_code.isdigit():
            return normalized_contract_code


def contract_clinet_type_code(callback_data):
    for word in callback_data.split():
        normalized_data = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_data.isdigit():
            yield normalized_data


# Делаем запрос в БД для проверки существования номера телефона и кому он принадлежит
def get_abonents_from_db(phone: str) -> list:
    result = DbConnection.execute_query(get_abonent_by_phonenumber_query, phone)
    return result


# Запросим баланс для указанного контракт кода
def get_balance_by_contract_code(contract_code: str):
    result = DbConnection.execute_query(getBalance_query, int(contract_code))
    return result


def get_client_services_list(contract_code, client_code, client_type_code):
    result = DbConnection.execute_query(
        f'exec MEDIATE..spWeb_GetClientServices {contract_code}, {client_code}, {client_type_code}')
    return result


def contract_code_by_userid(user_id: str):
    result = DbConnection.execute_query(get_phonenumber_by_user_id_query, user_id)
    phonenumber = result[0]['phonenumber'][-10:]
    return DbConnection.execute_query(get_abonent_by_phonenumber_query, phonenumber)


def get_prise(dice_value: int):
    return PRISE_ACTION[dice_value]

