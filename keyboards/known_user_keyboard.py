from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU
from icecream import ic
import copy
# ----------------------------------- Меню кнопок для пользователей ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text=LEXICON_RU['my_balance']), KeyboardButton(text=LEXICON_RU['my_services'])]
    , [KeyboardButton(text=LEXICON_RU['my_support_tickets']), KeyboardButton(text=LEXICON_RU['promised_payment'])]
    , [KeyboardButton(text=LEXICON_RU['inet_password']), KeyboardButton(text=LEXICON_RU['personal_area_password'])]
    # , [KeyboardButton(text=LEXICON_RU['drop_the_dice'])]
]

user_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def without_dice_kb_known_users() -> ReplyKeyboardMarkup:
    now_buttons = copy.copy(buttons)
    now_buttons.pop(3)
    return ReplyKeyboardMarkup(keyboard=now_buttons, resize_keyboard=True)
