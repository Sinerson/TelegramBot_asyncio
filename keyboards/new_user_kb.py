from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU
from icecream import ic

# ----------------------------------- Кнопка отправки контакта ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Отправить телефон", request_contact=True)]
]

new_user_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def make_keyboard_for_newbie(abonent_from_db, *phonenumber):
    button_list = []
    for dicts in abonent_from_db:
        button = []
        button.append(InlineKeyboardButton(text=f"{LEXICON_RU['contract']} {str(dicts['CONTRACT'])},"
                                                f" {LEXICON_RU['address']} {str(dicts['ADDRESS'])}",
                                           callback_data=f'ADD_NEW_USER {str(dicts["CONTRACT_CODE"])} {phonenumber[0]}'))
        button_list.append(button)
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=button_list)