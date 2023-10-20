from aiogram import Router
from aiogram.types import Message
from filters.filters import IsAdmin, admin_ids, IsKnownUsers, user_ids, manager_ids
from keyboards.admin_kb import admin_keyboard

admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids))
async def answer_if_admins_update(message: Message):
    if message.text != '/start':
        await message.answer(text="Хватит дурить! Сообщение не распознается!")
    else:
        await message.answer(text="Показываю меню:", reply_markup=admin_keyboard)
