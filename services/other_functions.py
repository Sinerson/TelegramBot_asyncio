import asyncio
import logging
from typing import Any

from redis import Redis
import pandas as pd
from icecream import ic

from db.fake_marketing_actions import PRISE_ACTION
from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, get_phonenumber_by_user_id_query, \
    getContractCode, get_all_users_query, PromisedPayDate, \
    getInetAccountPassword_query, getPersonalAreaPassword_query, \
    get_all_unbanned_users_query, get_all_known_unbanned_users_query, \
    getTechClaims_query, getContractCodeByUserId_query, add_client_properties_w_commentary, \
    add_client_properties_wo_commentary, getClientCodeByContractCode, update_unknown_user, checkUserExists, updateUser, \
    getHelpDeskClaims_query, getAbonNameByUserID_query, getFullAbonNameByUserID_query, \
    getFullAbonNameByContractCode_query
# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from settings import ExternalLinks, DbSecrets, BotSecrets


def add_new_known_user(user_id: int, chat_id: int, phonenumber: str, contract_code: int) -> bool:
    try:
        DbConnection.execute_query(
            f"exec MEDIATE..spAddNewUserTelegramBot {user_id},{chat_id},'{phonenumber}',{contract_code}")
        return True
    except Exception as e:
        # ic(e)
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
    result = DbConnection.execute_query(get_abonent_by_phonenumber_query, (phone,))
    return result


def get_abonent_name_by_user_id(user_id: int) -> list[dict]:
    """ Возвращает список словарей с полями USER_ID, CONTRACT_CODE, CONTRACT, FIRST_NAME, PATRONYMIC """
    result = DbConnection.execute_query(getAbonNameByUserID_query, (user_id,))
    # print(f'{result=}')
    return result


def get_full_abonent_name_by_user_id(user_id: int) -> list[dict]:
    """ Возвращает список словарей с полями USER_ID, CONTRACT_CODE, CONTRACT, LAST_NAME, FIRST_NAME, PATRONYMIC """
    result = DbConnection.execute_query(getFullAbonNameByUserID_query, (user_id,))
    return result


def get_full_abonent_name_by_contract_code(contract_code: int) -> list[dict]:
    # print(f"Получили contract_code: {contract_code}, тип данных: {type(contract_code)}")
    """ Возвращает список словарей с полями USER_ID, CONTRACT_CODE, CONTRACT, LAST_NAME, FIRST_NAME, PATRONYMIC,
    DEVICE """
    result = DbConnection.execute_query(getFullAbonNameByContractCode_query, (contract_code,))
    # print(f"{result=}")
    return result


# Запросим баланс для указанного контракт кода
def get_balance_by_contract_code(contract_code: str) -> list[dict]:
    try:
        result = DbConnection.execute_query(getBalance_query, (int(contract_code),))
        if result:
            return result
    except Exception as e:
        print(f"Ошибка в получении баланса: {e}")


def get_client_services_list(contract_code: int, client_code: int, client_type_code: int) -> list[dict]:
    """ Возвращает услуги абонента в виде списка словарей,
        при подаче кода контракта, кода клиента и типа клиента в виде int
    """
    if contract_code == 50323 and client_code == 50341 and client_type_code == 8:
        return [{'TARIFF_NAME': 'Для получения перечня услуг на л/с 500 обратитесь в отдел ОИТ', 'TARIFF_COST': 0}]
    else:
        try:
            return DbConnection.execute_query(
                f'exec MEDIATE..spWeb_GetClientServices {contract_code}, {client_code}, {client_type_code}'
            )
        except Exception as e:
            logging.error(f"Ошибка получения услуг абонента {e}")


def phone_number_by_userid(user_id: int) -> list:
    """ Возвращает номер телефона для существующих в БД пользователей по user_id"""
    result = DbConnection.execute_query(get_phonenumber_by_user_id_query, (user_id,))
    logging.info(f"переданный user_id: {user_id}, результат запроса к базе: {result}")
    phonenumber = result[0]['phonenumber'][-10:]
    result2 = DbConnection.execute_query(get_abonent_by_phonenumber_query, phonenumber)
    return result2


def contract_code_by_phone_for_new_users(phonenumber: str) -> list[dict]:
    """ Возвращает код контракта и номер контракта для пользоватей, не существующих в БД
        Ипользуется для поиска и добавления в БД новых абонентов, у которых телефон уже зарегистрирован
    """
    result = DbConnection.execute_query(getContractCode, (phonenumber,))
    return result[0]['CONTRACT_CODE']


def get_prise(dice_value: int) -> str:
    """ Тестовая заглушка, данные возвращает из словаря """
    return PRISE_ACTION[dice_value]


def get_prise_new(dice_value: int) -> str:
    """ Для работы с Google Spreadsheet через pandas"""
    # df = pd.read_csv(ExternalLinks.marketing_doc_link)
    df = pd.read_excel(ExternalLinks.marketing_doc_link, sheet_name="Акции")
    df_dict: dict = dict(zip(df.ACTION_ID, df.ACTION_NAME))
    return df_dict[dice_value]


def get_question_for_poll() -> tuple[list[Any], list[Any]]:
    df = pd.read_excel(ExternalLinks.marketing_doc_link, sheet_name="Опросы", engine="openpyxl")
    df_question = list(df['QUESTION'].dropna())
    df_answer_variants = list(df['ANSWER_VARIANTS'].dropna().drop_duplicates())
    return df_question, df_answer_variants


def get_question_for_quiz() -> tuple[list[Any], list[Any], list[Any]]:
    df = pd.read_excel(ExternalLinks.marketing_doc_link, sheet_name="Опросы", engine="openpyxl")
    df_question = list(df['QUESTION'].dropna())
    df_answer_variants = list(df['ANSWER_VARIANTS'].dropna().drop_duplicates())
    df_correct_answer = list(df['CORRECT_ANSWER'].dropna().drop_duplicates())
    return df_question, df_answer_variants, df_correct_answer


# def write_to_excel(filename: str, data: dict) -> Any:
#     try:
#         wb = Workbook()
#         ws = wb.active
#         ws.append(data)
#         wb.save(filename)
#         return (f"Write data to '{filename}' done!")
#     except Exception as e:
#         ic(e)
#         return e


def get_all_users_from_db() -> list[dict]:
    """ Получение всех пользователей из БД """
    result = DbConnection.execute_query(get_all_users_query)
    return result


def set_promised_payment(client_code: int) -> list:
    """ Вызов хранимой процедуры для установки свойства доверительного платежа """
    result = DbConnection.execute_query(f'exec MEDIATE..spMangoSetPromisedPay {client_code}')
    return result


def get_promised_pay_date(client_code: int) -> str:
    """ Установка доверительного платежа """
    result = DbConnection.execute_query(PromisedPayDate, (client_code,))
    f = lambda date: [res["DATE_CHANGE"] for res in date]
    return f(result)[0].strftime("%Y.%m.%d %H:%M")


def add_new_bot_admin(user_id: str) -> list[dict]:
    """ Возвращает  результат запроса в виде списка словаря в котором 0 или 1 по ключу RESULT """
    result = DbConnection.execute_query(f"exec MEDIATE..spAddNewAdminTelegramBot {user_id}")
    return result


def add_new_bot_manager(user_id: str) -> list[dict]:
    """ Возвращает  результат запроса в виде списка словаря в котором 0 или 1 по ключу RESULT """
    result = DbConnection.execute_query(f"exec MEDIATE..spAddNewManagerTelegramBot {user_id}")
    return result


def inet_account_password(contract_code: int) -> list[dict]:
    """ Возращаем логин и пароль от учетной записи интернет """
    result = DbConnection.execute_query(getInetAccountPassword_query, (contract_code,))
    return result


def personal_area_password(client_code: int) -> list[dict]:
    """ Возращаем логин и пароль от личного кабинета """
    result = DbConnection.execute_query(getPersonalAreaPassword_query, (client_code,))
    return result


def user_banned_bot_processing(user_id: int) -> list[dict]:
    """ Устанавливаем статус блокировки бота пользователем """
    result = DbConnection.execute_query(f"exec MEDIATE..spSetUserBlockedTelegramBot {user_id}")
    return result


def user_unbanned_bot_processing(user_id: int) -> list[dict]:
    """ Устанавливаем статус блокировки бота пользователем """
    result = DbConnection.execute_query(f"exec MEDIATE..spSetUserUnblockedTelegramBot {user_id}")
    return result


def get_list_unbanned_users() -> list:
    result = DbConnection.execute_query(get_all_unbanned_users_query)
    return result


def get_list_unbanned_known_users() -> list:
    result = DbConnection.execute_query(get_all_known_unbanned_users_query)
    return result


def notify_decline(user_id: int) -> bool:
    result = DbConnection.execute_query(f"exec MEDIATE..spDeclineWishNewsTelegramBot {user_id}")[0]['RESULT']
    if result != 1:
        return False
    else:
        return True


def get_tech_claims(contract_code: int) -> list[dict]:
    result = DbConnection.execute_query(getHelpDeskClaims_query, (contract_code,))
    return result


# Вариант получения данных из старой программы заявок ( Service Call )
# def get_tech_claims(contract_code: int) -> list[dict]:
#     result = DbConnection.execute_query(getTechClaims_query, contract_code)
#     return result


def get_contract_code_by_user_id(user_id: int) -> int:
    result = DbConnection.execute_query(getContractCodeByUserId_query, (str(user_id),))
    return result


def get_client_code_by_user_id(user_id: int) -> int:
    contract_code = int(get_contract_code_by_user_id(user_id)[0]['CONTRACT_CODE'])
    result = DbConnection.execute_query(getClientCodeByContractCode, (contract_code,))
    return int(result[0]['CLIENT_CODE'])


def insert_prise_to_db(user_id: int, prise: str) -> list[dict]:
    """ Функция добавления в таблицу с абонентами выбранного приза """
    result = DbConnection.execute_query(f"exec MEDIATE..spAddPriseFromTelegramBot {user_id},'{prise}'")
    return result


def insert_client_properties(client_code: int, prop_code: int, commentary: str = None) -> list[dict]:
    """ Вставка свойства абонента на основе кода свойства """
    if commentary:
        result = DbConnection.execute_query(add_client_properties_w_commentary, (client_code, prop_code, commentary,))
    else:
        result = DbConnection.execute_query(add_client_properties_wo_commentary, (client_code, prop_code,))
    return result


async def get_count_of_members_by_poll_variant(poll_id: str) -> tuple:
    conn_polls = Redis(host=DbSecrets.redis_host,
                       port=DbSecrets.redis_port,
                       db=1,
                       decode_responses=DbSecrets.redis_decode,
                       charset=DbSecrets.redis_charset
                       )
    conn_poll_answers = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=2,
                              decode_responses=DbSecrets.redis_decode,
                              charset=DbSecrets.redis_charset
                              )
    poll_name = conn_polls.get(poll_id)
    poll_answers = {}.fromkeys(get_question_for_poll()[1])
    poll_answers_count = len(poll_answers)
    cnt_values_in_answers = {}
    cnt = 0
    while cnt <= poll_answers_count - 1:
        for answer in poll_answers:
            cnt_values_in_answers[answer] = conn_poll_answers.scard(f'polls:{poll_id}:{cnt}')
            cnt += 1
    conn_polls.close()
    conn_poll_answers.close()
    return cnt_values_in_answers, poll_name


async def get_all_polls():
    conn_polls = Redis(host=DbSecrets.redis_host,
                       port=DbSecrets.redis_port,
                       db=1,
                       decode_responses=DbSecrets.redis_decode,
                       charset=DbSecrets.redis_charset
                       )
    polls: dict = {}.fromkeys(conn_polls.keys())
    for key in polls:
        polls[key] = conn_polls.get(key)
    return polls


def poll_id_from_callback(callback_data) -> any:
    """ Получаем из callback data номер опроса и отдаем его назад """
    for word in callback_data.split():
        normalized_contract_code = word.replace('.', '').replace(',', '').replace(' ', '').strip()
        if normalized_contract_code.isdigit():
            return normalized_contract_code


async def add_phone_for_unknown_user(user_id: str, chat_id: str, phonenumber: str):
    """ Функция сохраняет номер телефона пользователя, но не являющегося абонентом"""
    DbConnection.execute_query(update_unknown_user, (user_id, chat_id, phonenumber,))


async def check_user_is_exists(user_id: str) -> list:
    """ Проверим существование записи для user_id """
    result = DbConnection.execute_query(checkUserExists, (user_id,))
    return list(result)


async def convert_unknown_user_to_known(phonenumber: str, contract_code: int, user_id: int, chat_id: int) -> list:
    """ Обновление записи в БД для пользователя, который ранее обращался к боту, но его телефон не был найден в
    биллинге"""
    logging.info(f"phonenumber: {phonenumber}, contract_code: {contract_code}, user_id: {user_id}, chat_id: {chat_id}")
    result = DbConnection.execute_query(updateUser, (phonenumber, contract_code, user_id, chat_id,))
    return result


async def check_ban_by_user(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        from datetime import datetime
        logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Процесс проверки пользователей запущен")
        from aiogram import Bot
        from aiogram.methods.send_chat_action import SendChatAction
        from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
        bot = Bot(token=BotSecrets.bot_token, parse_mode="HTML")
        users = get_list_unbanned_known_users()
        for user in users:
            try:
                await bot(SendChatAction(chat_id=user['user_id'], action='typing'))
            except TelegramForbiddenError:
                user_banned_bot_processing(user['user_id'])
            except TelegramBadRequest:
                logging.error(f"Для пользователя {user['user_id']} нет чата")
