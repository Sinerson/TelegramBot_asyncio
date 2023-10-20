from aiogram import Router, F
from aiogram.types import Message
from filters.filters import NewUser, user_ids, admin_ids, manager_ids

from keyboards.new_user_kb import new_user_keyboard

new_user_rt = Router()


# Хэндлер на команду /start для новых пользователей
@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids))
async def cmd_start(message: Message):
    await message.answer(text="Новый пользователь",
                         reply_markup=new_user_keyboard)


@