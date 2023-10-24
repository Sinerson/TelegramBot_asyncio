from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command
from icecream import ic

from filters.filters import IsAdmin, admin_ids, IsKnownUsers, user_ids, manager_ids
from keyboards.admin_kb import menu_keyboard, choose_abonent_kb
from services.admin_users import get_abonents_from_db

admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'),
                  F.content_type != ContentType.CONTACT)
async def answer_if_admins_update(message: Message):
    await message.answer(text="Меню команд:", reply_markup=menu_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT)
async def get_contact_from_admin(message: Message):
    phone = message.contact.phone_number[-10:] # Берем последние 10 цифр из номера
    result = get_abonents_from_db(phone) # Ищем абонентов с совпадающим номером в БД
    count = len(result) # Получим количество абонентов в выборке
    #cnt = count # Какая-то переменная
    if count > 0: # Если у нас в выборку кто-то попал, тогда
        if count == 1: # Проверяем количество записей
            await message.answer(message.from_user.id,
                                 text=f"Найден 1 абонент! CLIENT_CODE: {result[0]['CLIENT_CODE']}, Phone: {result[0]['DEVICE']}")
        else:
            # while count > 0:
            await message.answer("Найдено более одного абонента, к которым привязан телефон, выберите нужного",
                                 reply_markup=choose_abonent_kb)
            ic(result)
            # await message.answer(f"Абонентов найдено: {cnt}! {count} из {cnt}: CLIENT_CODE: {result[count-1]['CLIENT_CODE']}, Phone: {result[count-1]['DEVICE']}")
        #    count -= 1

    else: # Если в выборке никого нет, сообщим пользователю
        await message.answer("Совпадений по номеру телефона не найдено!")


@admin_rt.callback_query(F.data.in_(['big_button_1_pressed', 'big_button_2_pressed']))
async def callback_answer(callback: CallbackQuery):
    await callback.answer()
