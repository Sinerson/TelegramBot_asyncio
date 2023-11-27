from asyncio import sleep
from db.redis import RedisConnector
from aiogram.methods import SendPoll
from icecream import ic
from main import dp
import pandas
import openpyxl
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ContentType, CallbackQuery

from filters.filters import IsAdmin, IsKnownUsers, user_ids, manager_ids, admin_ids
from keyboards.admin_kb import menu_keyboard, make_keyboard, keyboard_with_contract_client_type_code, \
    yes_no_keyboard, without_dice_kb, stop_spam_kb
from lexicon.lexicon_ru import LEXICON_RU
from main import bot
from services.classes import FSMFillForm
from services.other_functions import get_abonents_from_db, get_balance_by_contract_code, contract_code_from_callback, \
    get_client_services_list, phone_number_by_userid, contract_client_type_code_from_callback, \
    get_prise_new, set_promised_payment, get_promised_pay_date, add_new_bot_admin, add_new_bot_manager, \
    user_unbanned_bot_processing, get_list_unbanned_users, notify_decline, get_list_unbanned_known_users, \
    get_question_for_poll, get_question_for_quiz

admin_rt = Router()

connect = RedisConnector().create_connection(database=1)

# region Command Start
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  Command(commands='start'),
                  F.content_type != ContentType.CONTACT,
                  StateFilter(default_state)
                  )
async def _answer_if_admins_update(message: Message):
    """ Хэндлер для команды start от пользователей в группе администраторы """
    user_unbanned_bot_processing(message.from_user.id)
    await message.answer(text=LEXICON_RU['admin_menu'], reply_markup=menu_keyboard)


# endregion

# region Abonent balance
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT,
                  StateFilter(default_state))
async def _balance_request_contact_processing(message: Message):
    """ Хэндлер на поступившее сообщение от администратора, содержащее контактную информацию
    Администраторы могут узнавать баланс любого пользователя """
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


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("BALANCE"),
                         StateFilter(default_state))
async def _balance_answer(callback: CallbackQuery):
    """ Ответ на запрос баланса """
    balance: list[dict] = get_balance_by_contract_code(contract_code_from_callback(callback.data))
    for el in balance:
        await callback.message.edit_text(
            text=f"{LEXICON_RU['balance_is']} {round(int(el['EO_MONEY']), 2)} {LEXICON_RU['rubles']}",
            parse_mode='HTML')
        await callback.answer()


# endregion

# region Dice
@admin_rt.message(IsAdmin(admin_ids),
                  # IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['drop_the_dice'].lower(),
                  StateFilter(default_state))
async def _send_dice(message: Message):
    """ Отсылка игральной кости и получение значения которое выпало"""
    _dice = await message.answer_dice()
    prise: str = get_prise_new(_dice.dice.value)
    await sleep(4)
    yn_keyboard = yes_no_keyboard(_dice.dice.value)
    await message.answer(text=f"{LEXICON_RU['your_prise']} ||__*{prise}*__||\n{LEXICON_RU['do_make_a_choice']}",
                         reply_markup=yn_keyboard, parse_mode='MarkdownV2')


@admin_rt.callback_query(IsAdmin(admin_ids),
                         # IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("DICE"),
                         StateFilter(default_state)
                         )
async def _dice_callback(callback: CallbackQuery):
    """ Выбор или отказ от выбора для кубика """
    callback_data = callback.data.split()
    if 'yes' in callback_data:
        kb_without_dice = without_dice_kb()
        prise_action = get_prise_new(int(" ".join(callback_data[-1:])))
        #
        # TODO: нужна функция для добавления свойства на абонента.
        #  Свойство с комментарием в виде выбранного варианта выигрыша
        #
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

# region Poll ( regular + quiz )
@admin_rt.message(IsAdmin(admin_ids),
                  F.text.lower() == LEXICON_RU['make_poll'].lower(),
                  StateFilter(default_state))
async def _send_poll_regular(message: Message) -> None:
    """ Отправка опроса, созданной через Pandas DataFrame Google Spreadsheets
        и запись номера опроса в Redis """
    # подготовим данные
    _poll: tuple = get_question_for_poll()
    _question = _poll[0]
    _answers = _poll[1]
    result: Message = await bot(SendPoll(chat_id=message.chat.id,
                                         question=_question[0],
                                         options=_answers,
                                         is_anonymous=False,
                                         disable_notification=True,
                                         type='regular', # Тип: голосование
                                         protect_content=True #  Запрет на пересылку в другие чаты
                                         ))
    # Запишем с Redis
    connect.set(name=result.poll.id, value=_poll[0][0])



@admin_rt.message(IsAdmin(admin_ids),
                  F.text.lower() == LEXICON_RU['make_quiz'].lower(),
                  StateFilter(default_state))
async def _send_poll_quiz(message: Message):
    """ Отправка викторины, созданной через Pandas """
    # подготовим данные
    _poll: tuple = get_question_for_quiz()
    _question = _poll[0]
    _answers = _poll[1]
    _correct_answer = _poll[2]
    result: Message = await bot(SendPoll(chat_id=message.chat.id,
                                         question=_question[0],
                                         options=_answers,
                                         correct_option_id=2,
                                         is_anonymous=False,
                                         disable_notification=True,
                                         type='quiz',
                                         protect_content=True
                                         ))
    ic(result.poll.id)
    ic(result.poll.total_voter_count)


# endregion

# region Add Admin
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT,
                  StateFilter(FSMFillForm.fill_id_admin)
                  )
async def _fsm_contact_admin_processing(message: Message, state: FSMContext):
    if not message.contact.user_id:
        await message.answer(text=LEXICON_RU['not_a_telegram_user'])
        await state.clear()
    else:
        result = add_new_bot_admin(user_id=str(message.contact.user_id))
        if result[0]['RESULT'] == 1:
            await message.answer(
                f"Пользователь {message.contact.first_name} отмечен как администратор бота")
            await bot.send_message(chat_id=message.contact.user_id,
                                   text=f"Пользователь {message.from_user.first_name} добавил вас в администраторы бота. Для обновления меню нажмите /start")
            await state.clear()
        elif result[0]['RESULT'] == 2:
            await message.answer(f"Пользователь уже администратор")
            await state.clear()
        else:
            await message.answer(f"Пользователь не обращался к боту и его нет в БД.")
            await state.clear()


@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['add_admin'].lower(),
                  StateFilter(default_state)
                  )
async def _admin_add_state(message: Message, state: FSMContext):
    await message.answer(f"{LEXICON_RU['send_me_new_admin_id']} {LEXICON_RU['cancel_action']}")
    # Устанавливаем состояние ожидания ввода id
    await state.set_state(FSMFillForm.fill_id_admin)


@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  StateFilter(FSMFillForm.fill_id_admin),
                  F.text.isdigit()
                  )
async def _admin_add_process(message: Message, state: FSMContext):
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


# endregion

# region Del Admin

# endregion

# region Add Manager
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.content_type == ContentType.CONTACT,
                  StateFilter(FSMFillForm.fill_id_manager)
                  )
async def _fsm_contact_manager_processing(message: Message, state: FSMContext):
    if not message.contact.user_id:
        await message.answer(text=LEXICON_RU['not_a_telegram_user'])
        await state.clear()
    else:
        result = add_new_bot_manager(user_id=str(message.contact.user_id))
        if result[0]['RESULT'] == 1:
            await message.answer(f"Пользователь {message.contact.first_name} отмечен как менеджер бота")
            await bot.send_message(chat_id=message.contact.user_id,
                                   text=f"Пользователь {message.from_user.first_name}"
                                        f" добавил вас в менеджеры бота. Для обновления меню нажмите /start")
            await state.clear()  # Выходим из машины состояний
        elif result[0]['RESULT'] == 2:
            await message.answer(f"Пользователь уже менеджер")
            await state.clear()
        else:
            await message.answer(f"Пользователь не обращался к боту и его нет в БД.")
            await state.clear()


@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['add_manager'].lower(),
                  StateFilter(default_state)
                  )
async def _manager_add_state(message: Message, state: FSMContext):
    await message.answer(f"{LEXICON_RU['send_me_new_manager_id']} {LEXICON_RU['cancel_action']}")
    # Устанавливаем состояние ожидания ввода id
    await state.set_state(FSMFillForm.fill_id_manager)


@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  StateFilter(FSMFillForm.fill_id_manager),
                  F.text.isdigit()
                  )
async def _manager_add_requst(message: Message, state: FSMContext):
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


# endregion

# region Send message to user
@admin_rt.message(IsAdmin(admin_ids),
                  # IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['make_a_spam'].lower(),
                  StateFilter(default_state)
                  )
async def _send_message_to_users_request(message: Message, state: FSMContext):
    await message.answer(f"{LEXICON_RU['send_me_message_to_send']} {LEXICON_RU['cancel_action']}")
    # Устанавливаем состояние ожидания ввода сообщения для рассылки пользователям
    await state.set_state(FSMFillForm.fill_message_to_send)


@admin_rt.message(IsAdmin(admin_ids),
                  # IsKnownUsers(user_ids, admin_ids, manager_ids),
                  StateFilter(FSMFillForm.fill_message_to_send),
                  ~Command(commands='cancel')
                  )
async def _send_message_to_user_processing(message: Message, state: FSMContext):
    """ Функция рассылки сообщений пользователям. Сейчас заглушена, и рассылка осуществляется через эхо- сообщение в
    целях безопасности и избежания спама. Для исключения бана со стороны Telegram,
    в "боевом" режиме установлена задержка 10 сообщений в секунду """
    user_list = get_list_unbanned_known_users()
    user_cnt = len(user_list)
    cnt = 0
    for user in user_list:
        while cnt < 1:
            # ic(user) {'user_id': '1000713266'}
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"{message.md_text}\n\n"
                                        f"`Для отказа от получения уведомлений, нажмите кнопку под сообщением`",
                                   reply_markup=stop_spam_kb(message.from_user.id),
                                   parse_mode='MarkdownV2',
                                   disable_notification=False)
            await sleep(0.01)
            cnt += 1
    await message.answer(text=f"Рассылка закончена, сообщение отправлено {cnt} пользователям\.",
                         parse_mode='MarkdownV2',
                         disable_notification=False)
    await state.clear()


# endregion

# region Client Services
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['my_services'].lower(),
                  StateFilter(default_state)
                  )
async def _client_services_request(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'SERVICES')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'SERVICES')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("SERVICES"),
                         StateFilter(default_state)
                         )  # Проверяем что колл-бэк начинается с нужного слова и пропускаем дальше
async def _client_services_answer(callback: CallbackQuery):
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


# endregion

# region Promised Payments
@admin_rt.message(IsAdmin(admin_ids),
                  IsKnownUsers(user_ids, admin_ids, manager_ids),
                  F.text.lower() == LEXICON_RU['promised_payment'].lower(),
                  StateFilter(default_state)
                  )
async def _promised_payment_request(message: Message):
    _abonents = phone_number_by_userid(message.from_user.id)
    if len(_abonents) > 1:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)
    else:
        keyboard = keyboard_with_contract_client_type_code(_abonents, 'PROMISED_PAYMENT')
        await message.answer(text=LEXICON_RU['choose_abonent'], reply_markup=keyboard)


@admin_rt.callback_query(IsAdmin(admin_ids),
                         IsKnownUsers(user_ids, admin_ids, manager_ids),
                         F.data.startswith("PROMISED_PAYMENT"),
                         StateFilter(default_state)
                         )
async def _promised_payment_answer(callback: CallbackQuery):
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


# endregion

# region Command Cancel for any states

# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии ожидания ввода сообщения для рассылки,
# и отключать машину состояний
@admin_rt.message(IsAdmin(admin_ids),
                  Command(commands='cancel'),
                  StateFilter(FSMFillForm.fill_message_to_send)
                  )
async def _process_command_state_cancellation(message: Message, state: FSMContext):
    await message.answer(text='Вы отказались от рассылки пользователям! Можете начать сначала.\n\n')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии ожидания получения данных нового админа,
# и отключать машину состояний
@admin_rt.message(IsAdmin(admin_ids),
                  Command(commands='cancel'),
                  StateFilter(FSMFillForm.fill_id_admin)
                  )
async def _process_command_state_cancellation(message: Message, state: FSMContext):
    await message.answer(text='Вы прервали добавление нового администратора! Можете начать сначала.\n\n')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии ожидания получения данных нового менеджера,
# и отключать машину состояний
@admin_rt.message(IsAdmin(admin_ids),
                  Command(commands='cancel'),
                  StateFilter(FSMFillForm.fill_id_manager)
                  )
async def _process_command_state_cancellation(message: Message, state: FSMContext):
    await message.answer(text='Вы прервали добавление нового менеджера! Можете начать сначала.\n\n')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@admin_rt.message(Command(commands='cancel'), ~StateFilter(default_state))
async def _process_command_state_cancellation(message: Message, state: FSMContext):
    await message.answer(text='Вы прервали ввод данных! Можете начать сначала.\n\n')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()
# endregion
