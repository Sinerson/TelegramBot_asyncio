import pandas as pd
from icecream import ic
from db.fake_marketing_actions import PRISE_ACTION

from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, getClientCodeByContractCode, \
    get_phonenumber_by_user_id_query, getContractCode, get_all_users, PromisedPayDate, set_admin_query, \
    set_manager_query, addUser_query, getInetAccountPassword_query, getPersonalAreaPassword_query
from db.sybase import DbConnection

from settings import ExternalLinks


def add_new_known_user(user_id: int, chat_id: int, phonenumber: str, contract_code: int) -> bool:
    try:
        DbConnection.execute_query(addUser_query, user_id, chat_id, phonenumber, contract_code)
        return True
    except Exception as e:
        ic(e)
        return False


def contract_code_from_callback(callback_data) -> any:
    """ Получаем из хэндлера callback data и выделяем из нее код контракта, после чего отдаем его назад """
    for word in callback_data.split():
        normalized_contract_code = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_contract_code.isdigit():
            return normalized_contract_code


def contract_client_type_code_from_callback(callback_data: str) -> any:
    """ Возвращаем CONTRACT_CODE, CLIENT_CODE, TYPE_CODE в виде генераторных значений
        Для этого переданную строку callback делим на части и нормализуем, удалим возможные знаки
        препинания. После этого перебираем получившиеся части и проверяем являются ли они
        числовыми символами, если да - приводим к int и возвращаем по одному.
    """
    for word in callback_data.split():
        normalized_data = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_data.isdigit():
            yield int(normalized_data)


# Делаем запрос в БД для проверки существования номера телефона и кому он принадлежит
def get_abonents_from_db(phone: str) -> list[dict]:
    """ Функция  возвращает из БД данные по абоненту в виде списка словарей.
        На вход принимает телефонный номер в виде строки
    """
    result = DbConnection.execute_query(get_abonent_by_phonenumber_query, phone)
    return result


# Запросим баланс для указанного контракт кода
def get_balance_by_contract_code(contract_code: str) -> list:
    result = DbConnection.execute_query(getBalance_query, int(contract_code))
    return result


def get_client_services_list(contract_code: int, client_code: int, client_type_code: int) -> list[dict]:
    """ Возвращает услуги абонента в виде списка словарей,
        при подаче кода контракта, кода клиента и типа клиента в виде int
    """
    result = DbConnection.execute_query(
        f'exec MEDIATE..spWeb_GetClientServices {contract_code}, {client_code}, {client_type_code}')
    return result


def phone_number_by_userid(user_id: int) -> list:
    """ Возвращает номер телефона для сущесвующих в БД пользователей по user_id"""
    result = DbConnection.execute_query(get_phonenumber_by_user_id_query, user_id)
    phonenumber = result[0]['phonenumber'][-10:]
    return DbConnection.execute_query(get_abonent_by_phonenumber_query, phonenumber)


def contract_code_by_phone_for_new_users(phonenumber: str) -> list[dict]:
    """ Возвращает код контракта и номер контракта для пользоватей, не существующих в БД
        Ипользуется для поиска и добавления в БД новых абонентов, у которых телефон уже зарегистрирован
    """
    result = DbConnection.execute_query(getContractCode, phonenumber)
    ic(result)
    # return result[0]['CONTRACT_CODE']


def get_prise(dice_value: int) -> str:
    """ Тестовая заглушка, данные возвращает из словаря """
    return PRISE_ACTION[dice_value]


def get_prise_new(dice_value: int) -> str:
    """ Для работы с Google Spreadsheet через pandas"""
    df = pd.read_csv(ExternalLinks.marketing_doc_link)
    df_dict: dict = dict(zip(df.ACTION_ID, df.ACTION_NAME))
    return df_dict[dice_value]


def get_all_users_from_db() -> list[dict]:
    result = DbConnection.execute_query(get_all_users)
    return result


def set_promised_payment(client_code: int) -> list:
    """ Вызов хранимой процедуры для установки свойства доверительного платежа """
    result = DbConnection.execute_query(f'exec MEDIATE..spMangoSetPromisedPay {client_code}')
    return result


def get_promised_pay_date(client_code: int) -> str:
    result = DbConnection.execute_query(PromisedPayDate, client_code)
    f = lambda date: [res["DATE_CHANGE"] for res in date]
    return f(result)[0].strftime("%Y.%m.%d %H:%M")


def add_new_bot_admin(user_id: str) -> list[dict]:
    """ Возвращает  результат запроса в виде списка словаря в котором 0 или 1 по ключу RESULT """
    result = DbConnection.execute_query(set_admin_query, user_id)
    return result


def add_new_bot_manager(user_id: str) -> list[dict]:
    """ Возвращает  результат запроса в виде списка словаря в котором 0 или 1 по ключу RESULT """
    result = DbConnection.execute_query(set_manager_query, user_id)
    return result


def inet_account_password(contract_code: int) -> list[dict]:
    """ Возращаем логин и пароль от учетной записи интернет """
    result = DbConnection.execute_query(getInetAccountPassword_query, contract_code)
    return result


def personal_area_password(client_code: int) -> list[dict]:
    """ Возращаем логин и пароль от личного кабинета """
    result = DbConnection.execute_query(getPersonalAreaPassword_query, client_code)
    return result
