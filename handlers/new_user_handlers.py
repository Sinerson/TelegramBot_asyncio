import logging

import pyodbc
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ContentType, CallbackQuery
from icecream import ic

from filters.filters import NewUser, user_ids, manager_ids, admin_ids
from keyboards.new_user_kb import new_user_keyboard, make_keyboard_for_newbie
from keyboards.known_user_keyboard import user_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services.classes import FSMFillForm
from services.input_validator import validate_user_input
from services.mailer import send_email
from services.other_functions import add_new_known_user, get_abonents_from_db, \
    contract_client_type_code_from_callback, add_phone_for_unknown_user, check_user_is_exists, \
    convert_unknown_user_to_known

new_user_rt = Router()


# region команда Start
# Хэндлер на команду /start для новых пользователей
@new_user_rt.message(Command(commands='start'),
                     NewUser(user_ids, admin_ids, manager_ids),
                     F.content_type != ContentType.CONTACT,
                     StateFilter(default_state)
                     )
async def cmd_start(message: Message, ):
    await message.answer(text=LEXICON_RU['new_user'], reply_markup=new_user_keyboard)


# Хэндлер при получении контактных данных от новых пользователей
@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids),
                     F.content_type == ContentType.CONTACT,
                     StateFilter(default_state)
                     )
async def adding_new_user(message: Message):
    if message.contact.phone_number is None:
        await message.answer(LEXICON_RU['user_havent_phone_in_profile'])
    elif message.contact.user_id != message.from_user.id:
        await message.answer(LEXICON_RU['balance_for_owner_only'])
    else:
        # contract_code = contract_code_by_phone_for_new_users(message.contact.phone_number)
        phone = message.contact.phone_number[-10:]  # Берем последние 10 цифр из номера
        abonent_from_db = get_abonents_from_db(phone)  # Ищем абонентов с совпадающим номером в БД
        count = len(abonent_from_db)  # Получим количество абонентов в выборке
        if not count:  # Если в выборке никого нет, сообщим пользователю
            await message.answer(LEXICON_RU["phone_not_found"], parse_mode='MarkdownV2')
            try:
                await add_phone_for_unknown_user(str(message.from_user.id), str(message.chat.id),
                                                 message.contact.phone_number)
            except pyodbc.IntegrityError:
                logging.error(f"Для пользователя {str(message.from_user.id)} с телефоном {str(phone)} уже есть запись"
                              f" в БД, но номер телефона не найден в биллинге")
        elif count == 1:  # Если у нас в выборку кто-то попал, тогда
            # keyboard = make_keyboard_for_newbie(abonent_from_db)
            # await message.answer(text=LEXICON_RU['click_the_button_under_message'], reply_markup=keyboard)
            # Проверим существование записи для данного user_id в базе:
            #       если нет, вставляем запись:
            exists_result = await check_user_is_exists(str(message.from_user.id))
            if exists_result[0]['E'] == 0:  #
                result = add_new_known_user(message.contact.user_id,
                                            message.chat.id,
                                            message.contact.phone_number,
                                            abonent_from_db[0]['CONTRACT_CODE'])
                if result is False:
                    await message.answer(
                        text="Произошла ошибка при попытке добавить вас в базу данных, попробуйте еще раз.")
                else:
                    await message.answer(text=f"Идентифицировали Вас по нашему биллингу, как :\n"
                                              f"__{abonent_from_db[0]['NAME']}__\n"
                                              f"лицевой счет №__{abonent_from_db[0]['CONTRACT']}__\n"
                                              f"Воспользуйтесь меню ниже",
                                         reply_markup=user_keyboard,
                                         parse_mode='MarkdownV2')
            #       если есть, обновляем запись:
            else:
                result = await convert_unknown_user_to_known(message.contact.phone_number,
                                                             abonent_from_db[0]['CONTRACT_CODE'],
                                                             message.from_user.id,
                                                             message.chat.id
                                                             )
                if result is False:
                    await message.answer(
                        text="Произошла ошибка при попытке добавить вас в базу данных, попробуйте еще раз.")
                else:
                    await message.answer(text=f"Идентифицировали Вас по нашему биллингу, как :\n"
                                              f"__{abonent_from_db[0]['NAME']}__\n"
                                              f"лицевой счет №__{abonent_from_db[0]['CONTRACT']}__\n"
                                              f"Воспользуйтесь меню ниже",
                                         reply_markup=user_keyboard,
                                         parse_mode='MarkdownV2')
        else:  # Вариант с выбором абонента
            keyboard = make_keyboard_for_newbie(abonent_from_db, phone)
            await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


# endregion

# region Обработка Callback
@new_user_rt.callback_query(NewUser(user_ids, admin_ids, manager_ids),
                            F.data.startswith("ADD_NEW_USER"),
                            StateFilter(default_state)
                            )
async def add_new_user_callback_processing(callback: CallbackQuery):
    contractcode_phonenumber = list(contract_client_type_code_from_callback(callback.data))
    try:
        result_add_newbie = add_new_known_user(callback.from_user.id,
                                               callback.message.chat.id,
                                               contractcode_phonenumber[1],  # номер телефона
                                               contractcode_phonenumber[0]  # contract_code
                                               )
    except Exception as e:
        ic(e)
    await callback.message.delete()
    await callback.message.answer(text="Вы добавлены в БД. Воспользуйтесь меню ниже", reply_markup=user_keyboard)
    await callback.answer()


# endregion

# region Заявка на подключение
@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids),
                     F.text.lower() == LEXICON_RU['new_services_request'].lower(),
                     StateFilter(default_state)
                     )
async def _client_new_services_request(message: Message, state: FSMContext):
    await message.answer(
        text="Введите свои данные через пробел: Фамилия Имя Отчетство Дата рождения(ДД.ММ.ГГГГ) Контактный "
             "телефон\nДля отмены нажмите /cancel")
    await state.set_state(FSMFillForm.new_connection_request_data)


@new_user_rt.message(NewUser(user_ids, admin_ids, manager_ids),
                     StateFilter(FSMFillForm.new_connection_request_data))
async def _client_send_personal_data(message: Message, state: FSMContext):
    try:
        await state.update_data(
            new_connection_request_data=message.text.replace(",", " ").replace("  ", " ").split(" "))
        data = await state.get_data()
        name, surname, patronymic, birthdate, phone = data['new_connection_request_data']

        if not validate_user_input(name, surname, patronymic, birthdate, phone):
            await message.answer("❌ Некорректные данные. Пожалуйста, проверьте ввод и попробуйте снова.")
            return
        message_data = "Фамилия: {}\n" \
                       "Имя: {}\n" \
                       "Отчество: {}\n" \
                       "Дата рождения: {}\n" \
                       "Телефон: {}\n".format(surname, name, patronymic, birthdate, phone)

        await message.answer(text="Получили данные\n"
                                  "Фамилия: {}\n"
                                  "Имя: {}\n"
                                  "Отчество: {}\n"
                                  "Дата рождения: {}\n"
                                  "Телефон: {}\n".format(
            surname, name, patronymic, birthdate, phone))

        # Отправим сообщение
        res = await send_email(message_data)
        # print(f"Отправили в mailer данные: {message_data}")
        if res == "success":
            await state.clear()
            await message.answer(text="Указанные данные будут переданы менеджеру. Ожидайте звонка в ближайшее время.")
        else:
            await state.clear()
            await message.answer(text=f"Ошибка отправки: {res}")

    except Exception as e:
        print(e)
        await message.answer(text="❌ Ошибка обработки данных. Пожалуйста, введите данные в формате: "
                                  "Имя Фамилия Отчество ДД.ММ.ГГГГ Телефон")

# endregion
