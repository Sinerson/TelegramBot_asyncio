from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command

from icecream import ic
from lexicon.lexicon_ru import LEXICON_RU
from asyncio import sleep

from filters.filters import IsAdmin, IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import menu_keyboard, make_keyboard, make_keyboard_for_services, yes_no_keyboard, del_dice_kb
from services.other_functions import get_abonents_from_db, get_balance_by_contract_code, contract_code_from_callback, \
    get_client_services_list, contract_code_by_userid, contract_clinet_type_code, get_prise

admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'),
                  F.content_type != ContentType.CONTACT)
async def answer_if_admins_update(message: Message):
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=menu_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT)
async def contact_processing(message: Message):
    phone = message.contact.phone_number[-10:]  # Берем последние 10 цифр из номера
    abonent_from_db = get_abonents_from_db(phone)  # Ищем абонентов с совпадающим номером в БД
    count = len(abonent_from_db)  # Получим количество абонентов в выборке
    if count == 1:  # Если у нас в выборку кто-то попал, тогда
        keyboard = make_keyboard(abonent_from_db)
        await message.answer(text=LEXICON_RU['click_the_button_under_message'], reply_markup=keyboard)
    elif count > 1:  # Вариант с выбором абонента
        keyboard = make_keyboard(abonent_from_db)
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:  # Если в выборке никого нет, сообщим пользователю
        await message.answer(LEXICON_RU["phone_not_found"])


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith(
                             "BALANCE"))  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def balance_answer(callback: CallbackQuery):
    balance = get_balance_by_contract_code(contract_code_from_callback(callback.data))
    for el in balance:
        await callback.message.edit_text(
            text=f"{LEXICON_RU['balance_is']} {round(int(el['EO_MONEY']), 2)} {LEXICON_RU['rubles']}", parse_mode='HTML')
            # reply_markup=callback.message.reply_markup, parse_mode='HTML')
        await callback.answer()


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith(
                             "SERVICES"))  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def services_answer(callback: CallbackQuery):
    abonents_data: list = list(map(int, contract_clinet_type_code(callback.data)))
    if abonents_data:
        services = get_client_services_list(abonents_data[0], abonents_data[1], abonents_data[2])
        services_list = []
        for el in services:
            services_list.append(
                f"{LEXICON_RU['service']}: {el['TARIFF_NAME']}, {LEXICON_RU['cost']}: {round(float(el['TARIFF_COST']), 2)} {LEXICON_RU['rubles']}")
        services_string = "\n".join(str(el) for el in services_list)
        await callback.message.edit_text(text=services_string, parse_mode='HTML')
    else:
        await callback.answer(text=LEXICON_RU['something_wrong'], show_alert=True)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['my_services'].lower())
async def client_services(message: Message):
    _abonents = contract_code_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = make_keyboard_for_services(_abonents)
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['drop_the_dice'].lower())
async def send_dice(message: Message):
    _dice = await message.answer_dice()
    prise: str = get_prise(_dice.dice.value)
    await sleep(4)
    yn_keyboard = yes_no_keyboard(prise)
    await message.answer(text=f"Ваш выигрыш: <b>{prise}</b>\nЗапомнить выбор?", reply_markup=yn_keyboard, parse_mode='HTML')


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),F.data.startswith("DICE"))
async def dice_callback(callback: CallbackQuery):
    callback_data = callback.data.split()
    if 'yes' in callback_data:
        prise_action = " ".join(callback_data[callback_data.index("yes") + 1:])
        ic(prise_action)
        await callback.message.edit_text(text=f"{LEXICON_RU['your_choice']} <u><b>{prise_action}</b></u> {LEXICON_RU['fixed_thanks']}", parse_mode='HTML')
        await callback.answer()
    elif 'no' in callback_data:
        await callback.message.edit_text(text="Вы отказались от выбора! Кидайте кубик еще раз!", parse_mode='HTML')
        await callback.answer()
