from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from services.classes import FSMFillForm
from main import bot

from icecream import ic
from lexicon.lexicon_ru import LEXICON_RU
from asyncio import sleep

from filters.filters import IsAdmin, IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import menu_keyboard, make_keyboard, keyboard_for_services_and_promised_payment, \
    yes_no_keyboard, without_dice_kb
from services.other_functions import get_abonents_from_db, get_balance_by_contract_code, contract_code_from_callback, \
    get_client_services_list, phone_number_by_userid, contract_client_type_code_from_callback, \
    get_prise, get_prise_new,set_promised_payment, get_promised_pay_date, add_new_bot_admin, add_new_bot_manager

admin_rt = Router()


# Проверка на админа
@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids), Command(commands='start'),
                  F.content_type != ContentType.CONTACT, StateFilter(default_state))
async def answer_if_admins_update(message: Message):
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=menu_keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT, StateFilter(default_state))
async def contact_processing(message: Message):
    if message.contact.user_id != message.from_user.id:
        await message.answer(text=LEXICON_RU['balance_for_owner_only'])
    else:
        phone = message.contact.phone_number[-10:]  # Берем последние 10 цифр из номера
        abonent_from_db = get_abonents_from_db(phone)  # Ищем абонентов с совпадающим номером в БД
        count = len(abonent_from_db)  # Получим количество абонентов в выборке
        if not count:  # Если в выборке никого нет, сообщим пользователю
            await message.answer(LEXICON_RU["phone_not_found"])
        elif count == 1:  # Если у нас в выборку кто-то попал, тогда
            keyboard = make_keyboard(abonent_from_db)
            await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)
        else:  # Вариант с выбором абонента
            keyboard = make_keyboard(abonent_from_db)
            await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT, StateFilter(FSMFillForm.fill_id_admin))
async def fsm_contact_admin_processing(message: Message, state: FSMContext):
    if not message.contact.user_id:
        await message.answer(text=LEXICON_RU['not_a_telegram_user'])
        await state.clear()
    else:
        result = add_new_bot_admin(user_id=str(message.contact.user_id))
        if result[0]['RESULT'] == 1:
            await message.answer(
                f"Пользователь {message.contact.first_name} {message.contact.last_name} отмечен как администратор бота")
            await bot.send_message(chat_id=message.contact.user_id,
                                   text=f"Пользователь {message.from_user.first_name} {message.from_user.last_name} добавил вас в администраторы бота. Для обновления меню нажмите /start")
            await state.clear()
        elif result[0]['RESULT'] == 2:
            await message.answer(f"Пользователь уже администратор")
            await state.clear()
        else:
            await message.answer(f"Пользователь не обращался к боту и его нет в БД.")
            await state.clear()


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT, StateFilter(FSMFillForm.fill_id_manager))
async def fsm_contact_manager_processing(message: Message, state: FSMContext):
    if not message.contact.user_id:
        await message.answer(text=LEXICON_RU['not_a_telegram_user'])
        await state.clear()
    else:
        result = add_new_bot_manager(user_id=str(message.contact.user_id))
        if result[0]['RESULT'] == 1:
            await message.answer(
                f"Пользователь {message.contact.first_name} {message.contact.last_name} отмечен как менеджер бота")
            await bot.send_message(chat_id=message.contact.user_id,
                                   text=f"Пользователь {message.from_user.first_name} {message.from_user.last_name} добавил вас в менеджеры бота. Для обновления меню нажмите /start")
            await state.clear()  # Выходим из машины состояний
        elif result[0]['RESULT'] == 2:
            await message.answer(f"Пользователь уже менеджер")
            await state.clear()
        else:
            await message.answer(f"Пользователь не обращался к боту и его нет в БД.")
            await state.clear()


@admin_rt.callback_query(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("BALANCE"), StateFilter(
        default_state))  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def balance_answer(callback: CallbackQuery):
    balance = get_balance_by_contract_code(contract_code_from_callback(callback.data))
    for el in balance:
        await callback.message.edit_text(
            text=f"{LEXICON_RU['balance_is']} {round(int(el['EO_MONEY']), 2)} {LEXICON_RU['rubles']}",
            parse_mode='HTML')
        await callback.answer()


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['my_services'].lower(), StateFilter(default_state))
async def client_services(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'SERVICES')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'SERVICES')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['promised_payment'].lower(), StateFilter(default_state))
async def promised_payment_set(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_for_services_and_promised_payment(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['drop_the_dice'].lower(), StateFilter(default_state))
async def send_dice(message: Message):
    _dice = await message.answer_dice()
    prise: str = get_prise_new(_dice.dice.value)
    await sleep(4)
    yn_keyboard = yes_no_keyboard(prise, _dice.dice.value)
    await message.answer(text=f"{LEXICON_RU['your_prise']} <b>{prise}</b>\n{LEXICON_RU['do_make_a_choice']}",
                         reply_markup=yn_keyboard, parse_mode='HTML')


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['add_admin'].lower(), StateFilter(default_state))
async def admin_add_state(message: Message, state: FSMContext):
    await message.answer(f"{LEXICON_RU['send_me_new_admin_id']} {LEXICON_RU['cancel_action']}")
    # Устанавливаем состояние ожидания ввода id
    await state.set_state(FSMFillForm.fill_id_admin)


@admin_rt.message(IsAdmin(admin_ids), IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['add_manager'].lower(), StateFilter(default_state))
async def manager_add_state(message: Message, state: FSMContext):
    await message.answer(f"{LEXICON_RU['send_me_new_manager_id']} {LEXICON_RU['cancel_action']}")
    # Устанавливаем состояние ожидания ввода id
    await state.set_state(FSMFillForm.fill_id_manager)


@admin_rt.message(
    IsAdmin(admin_ids),
    IsKnownUsers(user_ids, admin_ids, manager_ids),
    StateFilter(FSMFillForm.fill_id_admin),
    F.text.isdigit()
)
async def admin_add_process(message: Message, state: FSMContext):
    result = add_new_bot_admin(user_id=message.text)
    if result[0]['RESULT'] == 1:
        await message.answer(f"Пользователь {message.text} отмечен как администратор бота")
        await state.clear()
    elif result[0]['RESULT'] == 2:
        await message.answer(f"Пользователь уже администратор")
        await state.clear()
    else:
        await message.answer(f"Пользователь не обращался к боту и его нет в БД.")
        await state.clear()


@admin_rt.message(
    IsAdmin(admin_ids),
    IsKnownUsers(user_ids, admin_ids, manager_ids),
    StateFilter(FSMFillForm.fill_id_manager),
    F.text.isdigit()
)
async def manager_add_process(message: Message, state: FSMContext):
    result = add_new_bot_manager(user_id=message.text)
    if result[0]['RESULT'] == 1:
        await message.answer(f"Пользователь {message.text} отмечен как менеджер бота")
        await state.clear()
    elif result[0]['RESULT'] == 2:
        await message.answer(f"Пользователь уже менеджер")
        await state.clear()
    else:
        await message.answer(f"Пользователь не обращался к боту и его нет в БД.\n")
        await state.clear()


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("SERVICES"),
                         StateFilter(default_state)
                         )  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def services_answer(callback: CallbackQuery):
    abonents_data = list(contract_client_type_code_from_callback(callback.data))
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


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("DICE"),
                         StateFilter(default_state)
                         )
async def dice_callback(callback: CallbackQuery):
    """ Выбор или отказ от выбора для кубика """
    callback_data = callback.data.split()
    if 'yes' in callback_data:
        kb_without_dice = without_dice_kb()
        prise_action = " ".join(callback_data[callback_data.index("yes") + 1:-1])
        await callback.message.edit_text(text=f"{LEXICON_RU['your_choice']} <u><b>{prise_action}</b></u>",
                                         parse_mode='HTML')
        # await callback.answer()
        await callback.message.answer(text=f"{LEXICON_RU['thanks_for_choice']}", reply_markup=kb_without_dice)
    elif 'no' in callback_data:
        await callback.message.edit_text(text=LEXICON_RU['choice_not_made'], parse_mode='HTML')
        await callback.answer()


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("PROMISED_PAYMENT"),
                         StateFilter(default_state)
                         )
async def promised_payment_answer(callback: CallbackQuery):
    """ Хэндлер для обработки callback установки доверительного платежа """
    abonents_data: list = list(contract_client_type_code_from_callback(callback.data))
    if abonents_data:
        result = set_promised_payment(abonents_data[1])[0]
        if "RESULT" in result:
            if result["RESULT"].startswith('New record.') or result["RESULT"].startswith('Existing record.'):
                await callback.message.edit_text(text=LEXICON_RU['promised_pay_granted'], parse_mode='HTML')
        else:
            if result["ERROR"].startswith('Err1'):
                await callback.message.edit_text(text=LEXICON_RU['call_support_err1'], parse_mode='HTML')
            elif result["ERROR"].startswith('Err2'):
                await callback.message.edit_text(text=LEXICON_RU['call_support_err2'], parse_mode='HTML')
            elif result["ERROR"].startswith('Err3'):
                await callback.message.edit_text(text=LEXICON_RU['advance_client'], parse_mode='HTML')
            elif result["ERROR"].startswith('Err4'):
                prop_date = f'<u><b>{get_promised_pay_date(abonents_data[1])}</b></u>'
                await callback.message.edit_text(
                    text=f'{LEXICON_RU["less_than_one_month"]}{LEXICON_RU["prev_date"]} {prop_date}', parse_mode='HTML')
    else:
        await callback.answer(text=LEXICON_RU['something_wrong'], show_alert=True)


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@admin_rt.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы прервали ввод данных! Можете начать сначала.\n\n')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()
