import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import sys

load_dotenv()

platform = sys.platform


@dataclass
class BotSecrets:
    """ Класс содержит данные для использования бота """
    bot_token: str = os.getenv("TOKEN_DEV")
    # bot_token: str = os.getenv("TOKEN_PROD")
    # admin_id: str = os.getenv("ADMIN_USERS_LIST")
    # manager_id: str = os.getenv("MANAGER_ID_LIST")
    # user_id: str = os.getenv("USERS_LIST")


@dataclass
class GptSecrets:
    folder_id: str = os.getenv("FOLDER_ID")
    auth: str = os.getenv("YAGPT_TOKEN")
    modelUri = os.getenv("MODEL_URI")
    model_name = os.getenv("LITE_MODEL")


@dataclass
class DbSecrets:
    """ Класс содержит переменные для строки подключения к БД """
    if platform.startswith('linux'):
        driver = os.getenv("LINUX_DRIVER")
    else:
        driver = os.getenv("WIN_DRIVER")
    server: str = os.getenv("SERVER")
    port: str = os.getenv("PORT")
    db_name: str = os.getenv("DB_NAME")
    user: str = os.getenv("USER")
    password: str = os.getenv("PASSW")
    lang: str = os.getenv("LANGUAGE")
    cn_lifetime: str = os.getenv("CONN_LIFETIME")
    idle: str = os.getenv("IDLE")
    autocommit: str = os.getenv("AUTOCOMMIT")
    optimize_prepare: str = os.getenv("OPTIMIZE_PREPARE")
    dynamic_prepare: str = os.getenv("DYNAMIC_PREPARE")
    hostname: str = os.getenv("CLIENT_HOST_NAME_DEV")
    # hostname: str = os.getenv("CLIENT_HOST_NAME_PROD")
    proc_name: str = os.getenv("CLIENT_HOST_PROC")
    app_name: str = os.getenv("APPLICATION_NAME_DEV")
    # app_name: str = os.getenv("APPLICATION_NAME_PROD")
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = os.getenv("REDIS_PORT")
    redis_db: int = os.getenv("REDIS_DB")
    redis_decode: bool = os.getenv("REDIS_DECODE")
    redis_charset: str = os.getenv("REDIS_CHARSET")


@dataclass
class ExternalLinks:
    """ Класс содержит одну переменную, со ссылкой на документ Google Spreadsheet """
    marketing_doc_link: str = os.getenv("MARKETING_ACTION_LINK")


@dataclass
class Mailer:
    """ Переменные для уведомления по email о новых заявка на подключение услуг """
    smtp_server: str = os.getenv("SMTP_SERVER")
    port: int = os.getenv("SMTP_PORT")
    sender: str = os.getenv("SENDER_EMAIL")
    username: str = os.getenv("SENDER_AUTH_NAME")
    password: str = os.getenv("SENDER_AUTH_PASSW")
    subject: str = "Telegram. Новая заявка на подключение услуг."
    send_to: str = os.getenv('RECEPIENT_EMAIL')
    message_text: str = "Поступила новая заявка:"
