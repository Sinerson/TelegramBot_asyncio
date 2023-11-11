from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from icecream import ic
from lexicon.lexicon_ru import LEXICON_RU
from asyncio import sleep

from filters.filters import IsAdmin, IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import menu_keyboard, make_keyboard, keyboard_for_services_and_promised_payment, \
    yes_no_keyboard, without_dice_kb
from services.other_functions import get_abonents_from_db, get_balance_by_contract_code, contract_code_from_callback, \
    get_client_services_list, contract_code_by_userid, contract_clinet_type_code_from_callback, \
    get_prise, set_promised_payment, get_promised_pay_date

admin_rt = Router()

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}

# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'),
                  F.content_type != ContentType.CONTACT)
async def answer_if_admins_update(message: Message):
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=menu_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT)
async def contact_processing(message: Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer(text=LEXICON_RU['balance_for_owner_only'])
    else:
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


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['my_services'].lower())
async def client_services(message: Message):
    _abonents = contract_code_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'SERVICES')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['promised_payment'].lower())
async def promised_payment_set(message: Message):
    _abonents = contract_code_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['drop_the_dice'].lower())
async def send_dice(message: Message):
    _dice = await message.answer_dice()
    prise: str = get_prise(_dice.dice.value)
    await sleep(4)
    yn_keyboard = yes_no_keyboard(prise)
    await message.answer(text=f"{LEXICON_RU['your_prise']} <b>{prise}</b>\n{LEXICON_RU['do_make_a_choice']}",
                         reply_markup=yn_keyboard, parse_mode='HTML')


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['add_admin'].lower())
async def admin_add(message: Message):
    pass


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith(
                             "SERVICES"))  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def services_answer(callback: CallbackQuery):
    abonents_data = list(contract_clinet_type_code_from_callback(callback.data))
    if abonents_data:
        services = get_client_services_list(abonents_data[0], abonents_data[1], abonents_data[2])
        services_list = []
        cnt = 1
        for el in services:
            services_list.append(
                f"<b>{cnt})</b> {el['TARIFF_NAME']}, {LEXICON_RU['cost']}: {round(float(el['TARIFF_COST']), 2)} {LEXICON_RU['rubles']}")
            cnt += 1
        services_string = "\n".join(str(el) for el in services_list)
        await callback.message.edit_text(text=services_string, parse_mode='HTML')
    else:
        await callback.answer(text=LEXICON_RU['something_wrong'], show_alert=True)


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), F.data.startswith("DICE"))
async def dice_callback(callback: CallbackQuery):
    ''' Выбор или отказ от выбора для кубика '''
    callback_data = callback.data.split()
    if 'yes' in callback_data:
        # kb_without_dice = without_dice_kb()
        prise_action = " ".join(callback_data[callback_data.index("yes") + 1:])
        await callback.message.edit_text(text=f"{LEXICON_RU['your_choice']} <u><b>{prise_action}</b></u>"
                                              f" {LEXICON_RU['thanks_for_choice']}", parse_mode='HTML')
        await callback.answer()
    elif 'no' in callback_data:
        await callback.message.edit_text(text=LEXICON_RU['choice_not_made'], parse_mode='HTML')
        await callback.answer()


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith(
                             "PROMISED_PAYMENT"))
async def promised_payment_answer(callback: CallbackQuery):
    ''' Хэндлер для обработки callback установки доверительного платежа '''
    # abonents_data: list = list(map(int, contract_clinet_type_code_from_callback(callback.data)))
    abonents_data: list = list(contract_clinet_type_code_from_callback(callback.data))
    if abonents_data:
        result = set_promised_payment(abonents_data[1])[0]["ERROR"]
        if result.startswith('New record.') or result.startswith('Existing record.'):
            await callback.message.edit_text(text=LEXICON_RU['promised_pay_granted'], parse_mode='HTML')
        elif result.startswith('Err1'):
            await callback.message.edit_text(text=LEXICON_RU['call_support_err1'], parse_mode='HTML')
        elif result.startswith('Err2'):
            await callback.message.edit_text(text=LEXICON_RU['call_support_err2'], parse_mode='HTML')
        elif result.startswith('Err3'):
            await callback.message.edit_text(text=LEXICON_RU['advance_client'], parse_mode='HTML')
        elif result.startswith('Err4'):
            prop_date = f'<u><b>{get_promised_pay_date(abonents_data[1])}</b></u>'
            await callback.message.edit_text(text=f'{LEXICON_RU["less_than_one_month"]}{LEXICON_RU["prev_date"]} {prop_date}', parse_mode='HTML')
    else:
        await callback.answer(text=LEXICON_RU['something_wrong'], show_alert=True)
