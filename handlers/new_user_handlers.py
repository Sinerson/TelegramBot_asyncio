from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from filters.filters import NewUser, user_ids, manager_ids, admin_ids
from keyboards.new_user_kb import new_user_keyboard

new_user_rt = Router()


# Хэндлер на команду /start для новых пользователей
@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids),
                     F.content_type.CONTACT == False,
                     StateFilter(default_state)
                     )
async def cmd_start(message: Message):
    await message.answer(text=LEXICON_RU['new_user'],
                         reply_markup=new_user_keyboard)


@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids),
                     F.content_type == ContentType.CONTACT
                     )
async def get_contact_from_new_user(message: Message):
    if message.contact.phone_number is None:
        await message.answer(LEXICON_RU['user_havent_phone_in_profile'])
    else:
        '''await message.answer(f'{LEXICON_RU["contact_data_get"]}: {message.contact.phone_number},'
                                                        f' {message.contact.first_name},'
                                                        f' {message.contact.last_name}')'''
