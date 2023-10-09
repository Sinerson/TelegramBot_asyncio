import logging
import os
from aiogram import Bot, Dispatcher
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Secrets():
    bot_token: str = os.getenv("TOKEN_DEV")
    admin_id: str = os.getenv("ADMIN_USERS_LIST")
    manager_id: str = os.getenv("MANAGER_ID_LIST")



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)

bot = Bot(token=Secrets.bot_token, parse_mode="HTML")
dp = Dispatcher()
