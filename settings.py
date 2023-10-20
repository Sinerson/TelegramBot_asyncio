import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Secrets:
    bot_token: str = os.getenv("TOKEN_DEV")
    admin_id: str = os.getenv("ADMIN_USERS_LIST")
    manager_id: str = os.getenv("MANAGER_ID_LIST")
    user_id: str = os.getenv("USERS_LIST")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
