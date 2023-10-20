from aiogram import Router, F
from aiogram.types import Message, ContentType

from filters.filters import NewUser, user_ids, admin_ids, manager_ids
from keyboards.new_user_kb import new_user_keyboard

new_user_rt = Router()


# Хэндлер на команду /start для новых пользователей
@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids), F.content_type.CONTACT == False)
async def cmd_start(message: Message):
    await message.answer(text="Новый пользователь",
                         reply_markup=new_user_keyboard)


@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids), F.content_type == ContentType.CONTACT)
async def get_contact_from_new_user(message: Message):
    if message.contact.phone_number is None:
        await message.answer("У вас не указан номер телефона!")
    else:
        await message.answer(f'получены контактые данные: {message.contact.phone_number},'
                                                        f' {message.contact.first_name},'
                                                        f' {message.contact.last_name}')
