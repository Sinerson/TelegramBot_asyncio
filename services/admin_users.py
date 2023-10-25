from icecream import ic

from db.sybase import DbConnection
from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, get_admin_query, get_manager_query


# Делаем запрос в БД для проверки существования номера телефона и кому он принадлежит
def get_abonents_from_db(phone: str) -> list:
    result = DbConnection.execute_query(get_abonent_by_phonenumber_query, phone)
    return result


# Запросим баланс для указанного контракт кода
def get_balance_by_contract_code(contract_code: str):
    result = DbConnection.execute_query(getBalance_query, int(contract_code))
    return result


# Получаем из хэндлера callback data и выделяем из нее код контракта, после чего отдаем его назад
def contract_code_from_callback(callback_data):
    for word in callback_data.split():
        normalized_contract_code = word.replace('.', '').replace(',', '').strip()
        if normalized_contract_code.isdigit():
            return normalized_contract_code


def get_admins() -> list:
    result = DbConnection.execute_query(get_admin_query)
    admin_ids = []
    for el in result:
        admin_ids.append(list(el.values())[0])
    return list(map(int, admin_ids))


def get_manager() -> list:
    result = DbConnection.execute_query(get_manager_query)
    manager_ids = []
    for el in result:
        manager_ids.append(list(el.values())[0])
    return list(map(int, manager_ids))
