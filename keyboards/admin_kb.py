from icecream import ic
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Послать сообщение пользователям бота")],
    [KeyboardButton(text="Проверка связи с БД", request_contact=True)],
    [KeyboardButton(text="Добавить менеджера"), KeyboardButton(text="Добавить админа")],
    [KeyboardButton(text="Мой баланс"), KeyboardButton(text="Мои услуги")]
]

menu_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


'''def get_inline_buttons(*args):
    inline_buttons = []
    for v in args:
        sub = v.split(",")
        inline_buttons.append(sub)
    ic()
    return InlineKeyboardMarkup(inline_buttons)
'''
url_button_1 = InlineKeyboardButton(text='ул.Кстовская 5-31', callback_data='big_button_1_pressed')
url_button_2 = InlineKeyboardButton(text='ул.Глебова 4-', callback_data='big_button_1_pressed')

choose_abonent_kb = InlineKeyboardMarkup(inline_keyboard=[
    [url_button_1],
    [url_button_2]
])
