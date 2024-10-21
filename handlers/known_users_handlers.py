import logging
from asyncio import sleep
import pyodbc
from icecream import ic
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from filters.filters import IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import keyboard_with_contract_client_type_code, yes_no_keyboard
from keyboards.known_user_keyboard import user_keyboard, without_dice_kb_known_users, survey_list_kb, survey_grade_choose
from keyboards.new_user_kb import new_user_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services.other_functions import get_balance_by_contract_code, contract_code_from_callback, \
    get_client_services_list, phone_number_by_userid, contract_client_type_code_from_callback, \
    get_prise_new, set_promised_payment, get_promised_pay_date, inet_account_password, personal_area_password, \
    user_unbanned_bot_processing, notify_decline, get_contract_code_by_user_id, get_tech_claims, insert_prise_to_db, \
    insert_client_properties, get_client_code_by_user_id
from services.classes import FSMFillForm
from services.surveys import get_all_surveys, insert_grade, get_available_surveys, get_survey_description,\
    get_all_surveys_voted_by_user, insert_grade_as_commentary


user_rt = Router()


# region Commnd Start
# Хэндлер на команду /start для простых пользователей
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 Command(commands='start'),
                 StateFilter(default_state)
                 )
async def cmd_start(message: Message):
    user_unbanned_bot_processing(message.from_user.id)
    await message.answer(text=LEXICON_RU['for_use_bot_push_button'],
                         reply_markup=user_keyboard)


# endregion

# region Balance
# Хэндлер на команду запроса баланса
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['my_balance'].lower(),
                 StateFilter(default_state))
async def known_client_balance_request(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'BALANCE')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'BALANCE')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


# Обработка callback для баланса
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("BALANCE"),
                        StateFilter(default_state)
                        )
async def balance_answer(callback: CallbackQuery):
    balance = get_balance_by_contract_code(contract_code_from_callback(callback.data))
    for el in balance:
        total_balance = round(float(el['TTL_EO_MONEY']) + float(el['PROPNACH_MONEY']), 2)
        services_balance = round(float(el['OSNUSL_MONEY']), 2)
        installment_balance = round(float(el['SELL_MONEY']), 2)
        if installment_balance:
            message_text = (
                f"{LEXICON_RU['balance_is']}\n"
                f"общий: {total_balance} {LEXICON_RU['rubles']}\n"
                f"услуги: {services_balance} {LEXICON_RU['rubles']}\n"
                f"рассрочка: {installment_balance} {LEXICON_RU['rubles']}"
            )
        else:
            message_text = (
                f"{LEXICON_RU['balance_is']}\n"
                f"общий: {total_balance} {LEXICON_RU['rubles']}\n"
                f"услуги: {services_balance} {LEXICON_RU['rubles']}\n"
            )
        await callback.message.edit_text(
            text=message_text,
            parse_mode='HTML'
        )
        await callback.answer()


# endregion

# region Client Services
# Хэндлер для запроса услуг
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['my_services'].lower(),
                 StateFilter(default_state)
                 )
async def client_services(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if not _abonents:
        logging.error(f"для пользователя user_id: {message.from_user.id} не найден номер телефона в таблице")
        await message.answer(text="Не найден номер телефона. Нажмите кнопку для отправки", reply_markup=new_user_keyboard)
    else:
        if len(_abonents) > 1:
            keyboard = keyboard_with_contract_client_type_code(_abonents, 'SERVICES')
            await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
        else:
            keyboard = keyboard_with_contract_client_type_code(_abonents, 'SERVICES')
            await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


# Обработка callback для запроса услуг
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("SERVICES"),
                        StateFilter(default_state)
                        )
async def services_answer(callback: CallbackQuery):
    abonents_data = list(contract_client_type_code_from_callback(callback.data))
    if abonents_data:
        services = get_client_services_list(abonents_data[0], abonents_data[1], abonents_data[2])
        services_list = []
        cnt = 1
        for el in services:
            if el['TARIFF_COST'] is None:
                services_list.append(f"<b>{cnt})</b> {el['TARIFF_NAME']}, {LEXICON_RU['cost']}: {'уточняйте е/м платеж'} {LEXICON_RU['rubles']}")
            else:
                services_list.append(f"<b>{cnt})</b> {el['TARIFF_NAME']}, {LEXICON_RU['cost']}: {round(float(el['TARIFF_COST']), 2)} {LEXICON_RU['rubles']}")
            cnt += 1
        services_string = "\n".join(str(el) for el in services_list)
        await callback.message.edit_text(text=services_string, parse_mode='HTML')
    else:
        await callback.answer(text=LEXICON_RU['something_wrong'], show_alert=True)


# endregion

# region Promised Payment
# Хэндлер для запроса доверительного платежа
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['promised_payment'].lower(),
                 StateFilter(default_state)
                 )
async def promised_payment_set(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


# Обработка коллбэка доверительного платежа
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("PROMISED_PAYMENT"),
                        StateFilter(default_state)
                        )
async def promised_payment_answer(callback: CallbackQuery):
    """ Хэндлер для обработки callback установки доверительного платежа """
    # abonents_data: list = list(map(int, contract_clinet_type_code_from_callback(callback.data)))
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


# endregion

# region Dice
# Хэндлер на запрос броска кубика
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['drop_the_dice'].lower(),
                 StateFilter(default_state)
                 )
async def send_dice(message: Message):
    _dice = await message.answer_dice()
    prise: str = get_prise_new(_dice.dice.value)
    await sleep(4)
    yn_keyboard = yes_no_keyboard(_dice.dice.value)
    await message.answer(text=f"{LEXICON_RU['your_prise']} ||*{prise}*||\n{LEXICON_RU['do_make_a_choice']}",
                         reply_markup=yn_keyboard, parse_mode='MarkdownV2')


# Обработка коллбэка для кубика
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("DICE"),
                        StateFilter(default_state)
                        )
async def dice_callback(callback: CallbackQuery):
    """ Выбор или отказ от выбора для кубика """
    callback_data = callback.data.split()
    if 'yes' in callback_data:
        kb_without_dice = without_dice_kb_known_users()
        prise_action = get_prise_new(int(" ".join(callback_data[-1:])))
        insert_prise_to_db(callback.from_user.id, prise_action)
        # TODO: Пока функционал навешивания свойства на абонента под вопросом, поэтому 2 строки ниже закомментил
        # client_code = get_client_code_by_user_id(callback.from_user.id)
        # insert_client_properties(client_code, 1138, prise_action)
        await callback.message.edit_text(
            text=f"{LEXICON_RU['your_choice']} <u><b><a href='https://sv-tel.ru'>{prise_action}</a></b></u>",
            parse_mode='HTML',
            disable_web_page_preview=True
            )
        await callback.message.answer(text=f"{LEXICON_RU['thanks_for_choice']}", reply_markup=kb_without_dice)
        await callback.answer()
    elif 'no' in callback_data:
        await callback.message.edit_text(text=LEXICON_RU['choice_not_made'], parse_mode='HTML')
        await callback.answer()


# endregion

# region Inet password
# Хэндлер на команду запроса пароля от аккаунта интернет
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['inet_password'].lower(),
                 StateFilter(default_state))
async def known_client_inet_password_request(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'INET_PASSWORD')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'INET_PASSWORD')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


# Обработка callback для пароля на интернет
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("INET_PASSWORD"),
                        StateFilter(default_state)
                        )
async def inet_password_answer(callback: CallbackQuery):
    result = inet_account_password(list(contract_client_type_code_from_callback(callback.data))[0])
    await callback.message.edit_text(text=f"*Имя пользователя:* `{result[0]['LOGIN']}`\n"
                                          f"*Пароль:* `{result[0]['PASSWORD']}`\n\n"
                                          f"Подробнее, как настроить PPPoE на роутере или компьютере, можете"
                                          f" [посмотреть на нашем сайте](https://sv-tel.ru/help/technical/)"
                                     , parse_mode='MarkdownV2', disable_web_page_preview=True)
    await callback.answer()


# Хэндлер на команду запроса пароля от ЛК
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['personal_area_password'].lower(),
                 StateFilter(default_state))
async def known_client_personal_area_password(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'LK')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'LK')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


# endregion

# region LK password
# Обработка callback для пароля от ЛК
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("LK"),
                        StateFilter(default_state)
                        )
async def personal_area_password_answer(callback: CallbackQuery):
    callback_parse = list(contract_client_type_code_from_callback(callback.data))
    result = personal_area_password(callback_parse[1])  # Вытащим по индексу CLIENT_CODE
    if not result:
        await callback.message.edit_text(text="Учетные данные не обнаружены, обратитесь в тех.поддержку.")
    else:
        if len(result) > 1:
            await callback.message.edit_text(text="Найдено несколько пар учетных данных. Можно использовать любые.")
            cnt = len(result)
            while cnt > 0:
                for el in result:
                    await callback.message.answer(
                        text=f"*Имя пользователя:* `{el['PIN']}`\n*Пароль:* `{el['PIN_PASSWORD']}`",
                        parse_mode='MarkdownV2'
                        )
                    cnt -= 1
            await callback.message.answer(
                text=f"Перейти в личный кабинет можно по <a href='https://bill.sv-tel.ru/'>ссылке</a>",
                parse_mode='HTML',
                disable_web_page_preview=True)
        else:
            await callback.message.edit_text(text=f"*Имя пользователя:* `{result[0]['PIN']}`\n"
                                                  f"*Пароль:* `{result[0]['PIN_PASSWORD']}`\n\n"
                                                  f"Перейти в личный кабинет можно по"
                                                  f" [ссылке](https://bill.sv-tel.ru)",
                                             parse_mode='MarkdownV2', disable_web_page_preview=True)
    await callback.answer()


# endregion

# region Stop get events
# Хэндлер обработки коллбэка прекращения подписки на рассылку (сама кнопка генерится в admin_handler.py)
@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("STOP_SPAM"),
                        StateFilter(default_state)
                        )
async def _unsubscribe_from_spam_result(callback: CallbackQuery):
    user_id = callback.from_user.id
    result = notify_decline(user_id)
    if result is True:
        await callback.message.edit_text(text=LEXICON_RU['unsubscribe_done'])
    else:
        await callback.message.edit_text(text=LEXICON_RU['service_notice'])
    await callback.answer()


# endregion

# region Support tickets
# Хэндлер для запроса заявок пользователя
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                 F.text.lower() == LEXICON_RU['my_support_tickets'].lower(),
                 StateFilter(default_state)
                 )
async def tech_claims_request(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'TECH_CLAIMS')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'TECH_CLAIMS')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                        F.data.startswith("TECH_CLAIMS"),
                        StateFilter(default_state)
                        )
async def tech_claims_answer(callback: CallbackQuery):
    """ Хэндлер для обработки callback на вывод заявок в тех.поддержку """
    abonents_data: list = list(contract_client_type_code_from_callback(callback.data))
    tech_claims = get_tech_claims(abonents_data[0])
    if not tech_claims:
        await callback.message.edit_text(text=LEXICON_RU['support_ticket_not_found'])
    else:
        await callback.message.edit_text(
            text=f"{LEXICON_RU['last_7days_tickets']}\n", parse_mode='MarkdownV2')
        for claim in tech_claims:
            await callback.message.answer(text=f"Заявка №<b>{claim['CLAIM_NUM']}</b>\n"
                                               f"Текущий статус: <b>{claim['STATUS_NAME']}</b>\n"
            # f"Дата создания: *{claim['APPL_DATE_CREATE']}*\n"
            # f"Назначена дата выполнения: *{claim['APPL_DATE_RUN']}*\n"
                                               f"ФИО: <b>{claim['CLIENT_NAME']}</b>\n"
                                               f"Адрес: <b>{claim['ADDRESS_NAME']}</b>\n"
                                               f"Заявлено: <b>{claim['ERROR_NAME']}</b>\n"
                                               f"Доп.инфо: <b>{claim['INFO_PROBLEMS_NAME']}</b>",
                                          parse_mode='HTML')


# endregion

# region Commnd Help
# Хэндлер для команды /help
@user_rt.message(Command(commands=["help"]),
                 StateFilter(default_state)
                 )
async def cmd_help(message: Message):
    await message.answer("Раздел помощи. Пока пустой.")
# endregion


# region Опросы
@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['take_part_in_the_survey'].lower(),
                  StateFilter(default_state)
                  )
async def _client_survey_request(message: Message):
    survey_list = get_available_surveys(message.from_user.id)
    all_surveys = get_all_surveys()
    if len(all_surveys) == 0 or all_surveys is None:
        await message.answer(text="Доступные опросы не найдены")
        return None
    if len(survey_list) == 0:
        await message.answer(text=LEXICON_RU['survey_list_empty'])
        voted_surveys = get_all_surveys_voted_by_user(message.from_user.id)
        await message.answer(text="Ниже перечислены опросы, в которых вы принимали участие.\n", parse_mode='HTML')
        for survey in voted_surveys:
            await message.answer(
                text=f"<b>Опрос:</b> {survey['SURVEY_SHORT_NAME']}\n"
                     f" <b>Наименование:</b> {survey['SURVEY_LONG_NAME']}\n"
                     f" <b>Ответ:</b> {survey['GRADE']}\n"
                     f" <b>Дата участия:</b> {survey['DATE']}\n",
                parse_mode='HTML')
    else:
        keyboard = survey_list_kb(survey_list)
        await message.answer(text=LEXICON_RU['available_surveys'], reply_markup=keyboard)


@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("SURVEY_CHOOSE"),
                         StateFilter(default_state)
                         )  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def _client_survey_choose(callback: CallbackQuery, state: FSMContext):
    survey_id = int(callback.data.split()[1])
    survey_type = int(callback.data.split()[2])
    # проверим доступность опроса для пользователя

    grade_keyboard = survey_grade_choose(survey_id=survey_id)
    survey_description = get_survey_description(survey_id=survey_id)
    if survey_type == 1:
        await callback.message.edit_text(text=f"<b>{survey_description[0]['SURVEY_LONG_NAME']}</b>\n\n{LEXICON_RU['grade_the_survey']}",
                                     parse_mode='HTML',
                                     reply_markup=grade_keyboard
                                     )
    elif survey_type == 2:
        await callback.message.edit_text(text="Введите пожалуйста свой ответ\n Если передумали, нажмите /cancel")
        await state.set_state(FSMFillForm.fill_text_grade)
        FSMFillForm.fill_survey_id = survey_id

    else:
        await callback.answer(text="Получен некорректный тип опроса\n")

@user_rt.callback_query(IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("SURVEY_GRADE"),
                         StateFilter(default_state)
                         )  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def _client_set_survey_grade(callback: CallbackQuery):
    survey_id = int(callback.data.split()[1])
    survey_grade = int(callback.data.split()[2])
    user_id = callback.from_user.id
    try:
        result = insert_grade(survey_id=survey_id, user_id=user_id, grade=survey_grade)
    except pyodbc.IntegrityError:
        await callback.answer(text=LEXICON_RU['you_already_voted_in_survey'], show_alert=True)
    await callback.message.edit_text(text=LEXICON_RU['thank_you_for_vote'])
    await callback.answer(text=LEXICON_RU['you_vote_was_counted'], show_alert=True)


@user_rt.message(IsKnownUsers(user_ids, admin_ids, manager_ids),
                  StateFilter(FSMFillForm.fill_text_grade)
                  )  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def _client_set_text_survey_grade(message: Message, state: FSMContext):
    try:
        result = insert_grade_as_commentary(FSMFillForm.fill_survey_id, message.from_user.id, message.text)
        await state.clear()
        await message.answer(text="Благодарим за участие. Каждое мнение важно для нас.")
    except Exception as e:
        await message.answer(text=f"Повторите ввод")


# endregion