from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.user_keyboard import user_keyboard
from filters.filters import IsKnownUsers, user_ids, admin_ids, manager_ids

user_rt = Router()


# Хэндлер на команду /start
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'))
async def cmd_start(message: Message):
    await message.answer(text="Существующий пользователь. Не админ.", reply_markup=user_keyboard)


# Хэндлер для команды /help
@user_rt.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer("Раздел помощи")
