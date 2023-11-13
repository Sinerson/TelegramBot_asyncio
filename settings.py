import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotSecrets:
    bot_token: str = os.getenv("TOKEN_DEV")
    admin_id: str = os.getenv("ADMIN_USERS_LIST")
    manager_id: str = os.getenv("MANAGER_ID_LIST")
    user_id: str = os.getenv("USERS_LIST")


@dataclass
class DbSecrets:
    driver: str = os.getenv("DRIVER")
    server: str = os.getenv("SERVER")
    port: str = os.getenv("PORT")
    db_name: str = os.getenv("DB_NAME")
    user: str = os.getenv("USER")
    password: str = os.getenv("PASSW")
    lang: str = os.getenv("LANGUAGE")
    cn_lifetime: str = os.getenv("CONN_LIFETIME")
    idle: str = os.getenv("IDLE")
    autocommit: str = os.getenv("AUTOCOMMIT")
    hostname: str = os.getenv("CLIENT_HOST_NAME_DEV")
    proc_name: str = os.getenv("CLIENT_HOST_PROC")
    app_name: str = os.getenv("APPLICATION_NAME_DEV")


@dataclass
class ExternalLinks:
    marketing_doc_link: str = os.getenv("MARKETING_ACTION_LINK")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
