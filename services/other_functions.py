from icecream import ic
from db.fake_marketing_actions import PRISE_ACTION

from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, getClientCodeByContractCode, \
    get_phonenumber_by_user_id_query, getContractCode, get_all_users, PromisedPayDate
from db.sybase import DbConnection


# Получаем из хэндлера callback data и выделяем из нее код контракта, после чего отдаем его назад
def contract_code_from_callback(callback_data) -> int:
    for word in callback_data.split():
        normalized_contract_code = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_contract_code.isdigit():
            return normalized_contract_code


def contract_clinet_type_code_from_callback(callback_data: str) -> int:
    ''' Возвращаем CONTRACT_CODE, CLIENT_CODE, TYPE_CODE  в виде генераторных значений
        Для этого переданную строку callback делим на части и нормализуем, удалим возможные знаки
        препинания. После этого перебираем получившиеся части и проверяем являются ли они
        числовыми символами, если да - приводим к int и возвращаем по одному.
    '''
    for word in callback_data.split():
        normalized_data = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_data.isdigit():
            yield int(normalized_data)


# Делаем запрос в БД для проверки существования номера телефона и кому он принадлежит
def get_abonents_from_db(phone: str) -> list[dict]:
    ''' Функция  возвращает из БД данные по абоненту в виде списка словарей.
        НА вход принимает телефонный номер в виде строки
    '''
    result = DbConnection.execute_query(get_abonent_by_phonenumber_query, phone)
    return result


# Запросим баланс для указанного контракт кода
def get_balance_by_contract_code(contract_code: str) -> list:
    result = DbConnection.execute_query(getBalance_query, int(contract_code))
    return result


def get_client_services_list(contract_code: int, client_code: int, client_type_code: int) -> list[dict]:
    ''' Возвращает услуги абонента в виде списка словарей,
     при подаче кода контракта, кода клиента и типа клиента в виде int '''
    result = DbConnection.execute_query(
        f'exec MEDIATE..spWeb_GetClientServices {contract_code}, {client_code}, {client_type_code}')
    return result


def contract_code_by_userid(user_id: str) -> list:
    result = DbConnection.execute_query(get_phonenumber_by_user_id_query, user_id)
    phonenumber = result[0]['phonenumber'][-10:]
    return DbConnection.execute_query(get_abonent_by_phonenumber_query, phonenumber)


def get_prise(dice_value: int) -> str:
    return PRISE_ACTION[dice_value]


def get_all_users_from_db() -> list[dict]:
    result = DbConnection.execute_query(get_all_users)
    return result


def set_promised_payment(client_code: int) -> list:
    ''' Вызов хранимой процедуры для установки свойства доверительного платежа '''
    result = DbConnection.execute_query(f'exec MEDIATE..spMangoSetPromisedPay {client_code}')
    return result


def get_promised_pay_date(client_code: int) -> str:
    result = DbConnection.execute_query(PromisedPayDate, client_code)
    f = lambda date:[res["DATE_CHANGE"] for res in date]
    return f(result)[0].strftime("%Y.%m.%d %H:%M")