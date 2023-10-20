from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from filters.filters import IsAdmin, admin_ids, IsKnownUsers, user_ids, manager_ids
from keyboards.admin_kb import admin_keyboard
from services.admin_users import get_abonent_by_phonenumber


admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'), F.content_type != ContentType.CONTACT)
async def answer_if_admins_update(message: Message):
    await message.answer(text="Меню команд:", reply_markup=admin_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), F.content_type == ContentType.CONTACT)
async def get_contact_from_admin(message: Message):
    # Берем последние 10 цифр из номера
    phone = message.contact.phone_number[-10:]
    result = get_abonent_by_phonenumber(phone)
    # Получим количество абонентов в выборке
    count = len(result)
    # Какая-то переменная
    cnt = count
    # Если у нас в выборку кто-то попал, тогда
    if count is not None:
        # Проверяем количество записей
        if count == 1:
            print(f"Найден 1 абонент! CLIENT_CODE: {result[0]['CLIENT_CODE']}, Phone: {result[0]['DEVICE']}")
        else:
            while count > 0:
                print(f"Абонентов найдено: {cnt}! {count} из {cnt}: CLIENT_CODE: {result[count-1]['CLIENT_CODE']}, Phone: {result[count-1]['DEVICE']}")
                count -= 1
    else:
        print("Совпадение по номеру телефона не найдено!")
