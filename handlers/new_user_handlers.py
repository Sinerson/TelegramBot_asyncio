from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from filters.filters import NewUser, user_ids, manager_ids, admin_ids
from keyboards.new_user_kb import new_user_keyboard, make_keyboard_for_newbie
from keyboards.user_keyboard import user_keyboard
from services.other_functions import contract_code_by_phone_for_new_users, add_new_known_user, get_abonents_from_db,\
    contract_client_type_code_from_callback

from icecream import ic

new_user_rt = Router()


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
            await message.answer(LEXICON_RU["phone_not_found"])
        elif count == 1:  # Если у нас в выборку кто-то попал, тогда
            # keyboard = make_keyboard_for_newbie(abonent_from_db)
            # await message.answer(text=LEXICON_RU['click_the_button_under_message'], reply_markup=keyboard)
            result = add_new_known_user(message.contact.user_id,
                                        message.chat.id,
                                        message.contact.phone_number,
                                        abonent_from_db[0]['CONTRACT_CODE'])
            if result is False:
                await message.answer(text="Произошла ошибка при попытке добавить вас в базу данных, попробуйте еще раз.")
            else:
                await message.answer(text="Вы добавлены в БД. Воспользуйтесь меню ниже", reply_markup=user_keyboard)
        else:  # Вариант с выбором абонента
            keyboard = make_keyboard_for_newbie(abonent_from_db, phone)
            await message.answer(text=LEXICON_RU['phone_more_then_one_abonent'], reply_markup=keyboard)


@new_user_rt.callback_query(NewUser(user_ids, admin_ids, manager_ids),
                            F.data.startswith("ADD_NEW_USER"),
                            StateFilter(default_state)
                            )
async def add_new_user_callback_processing(callback: CallbackQuery):
    contractcode_phonenumber = list(contract_client_type_code_from_callback(callback.data))
    try:
        result_add_newbie = add_new_known_user(callback.from_user.id,
                                               callback.message.chat.id,
                                               contractcode_phonenumber[1],    # номер телефона
                                               contractcode_phonenumber[0]          # contract_code
                                               )
    except Exception as e:
        ic(e)
    await callback.message.delete()
    await callback.message.answer(text="Вы добавлены в БД. Воспользуйтесь меню ниже", reply_markup=user_keyboard)
    await callback.answer()
