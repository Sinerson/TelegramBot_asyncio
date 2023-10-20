from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

# ----------------------------------- Кнопка отправки контакта ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Отправить телефон", request_contact=True)]
]

new_user_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
