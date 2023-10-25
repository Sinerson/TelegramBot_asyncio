from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command
from icecream import ic
from lexicon.lexicon_ru import LEXICON_RU

from filters.filters import IsAdmin, IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import menu_keyboard, make_keyboard
from services.admin_users import get_abonents_from_db, get_balance_by_contract_code, contract_code_from_callback

admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'),
                  F.content_type != ContentType.CONTACT)
async def answer_if_admins_update(message: Message):
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=menu_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT)
async def get_contact_from_admin(message: Message):
    phone = message.contact.phone_number[-10:] # Берем последние 10 цифр из номера
    abonent_from_db = get_abonents_from_db(phone) # Ищем абонентов с совпадающим номером в БД
    count = len(abonent_from_db) # Получим количество абонентов в выборке
    # cnt = count - 1 # Какая-то переменная
    if count == 1: # Если у нас в выборку кто-то попал, тогда
        keyboard = make_keyboard(abonent_from_db)
        await message.answer(text=LEXICON_RU['click_the_button_under_message'], reply_markup=keyboard)
    elif count > 1: # Вариант с выбором абонента
        keyboard = make_keyboard(abonent_from_db)
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else: # Если в выборке никого нет, сообщим пользователю
        await message.answer(LEXICON_RU["phone_not_found"])


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("BALANCE")) # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def balance_answer(callback: CallbackQuery):
    balance = get_balance_by_contract_code(contract_code_from_callback(callback.data))
    for el in balance:
        await callback.message.edit_text(text=f"{LEXICON_RU['balance_is']} {el['EO_MONEY']}", reply_markup=callback.message.reply_markup)
