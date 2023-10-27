from icecream import ic
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU

# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text=LEXICON_RU['send_message_to_users']), KeyboardButton(text=LEXICON_RU['drop_the_dice'])],
    [KeyboardButton(text=LEXICON_RU['add_manager']), KeyboardButton(text=LEXICON_RU['add_admin'])],
    [KeyboardButton(text=LEXICON_RU['my_balance'], request_contact=True),
     KeyboardButton(text=LEXICON_RU['my_services'])],
    [KeyboardButton(text=LEXICON_RU['promised_payment'])]
]

menu_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def make_keyboard(abonent_from_db):
    button_list = []
    for dicts in abonent_from_db:
        button = []
        button.append(InlineKeyboardButton(text=f"{LEXICON_RU['contract']} {str(dicts['CONTRACT'])},"
                                                f" {LEXICON_RU['address']} {str(dicts['ADDRESS'])}",
                                           callback_data=f'BALANCE {str(dicts["CONTRACT_CODE"])}'))
        button_list.append(button)
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=button_list)

def make_keyboard_for_services(abonents_data):
    button_list = []
    for dicts in abonents_data:
        button = []
        button.append(InlineKeyboardButton(text=f"{LEXICON_RU['contract']} {str(dicts['CONTRACT'])},"
                                                f" {LEXICON_RU['address']} {str(dicts['ADDRESS'])}",
                                           callback_data=f'SERVICES {str(dicts["CONTRACT_CODE"])}, {str(dicts["CLIENT_CODE"])}, {str(dicts["TYPE_CODE"])}'))
        button_list.append(button)
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=button_list)