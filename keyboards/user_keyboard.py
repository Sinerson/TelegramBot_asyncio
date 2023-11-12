from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

# ----------------------------------- Кнопка отправки контакта ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Баланс"),KeyboardButton(text="Услуги")],
    [KeyboardButton(text="Заявки в ТП")],
    [KeyboardButton(text="Доверительный платеж")],
    [KeyboardButton(text="Пароль от интернет"), KeyboardButton(text="Пароль от ЛК")]
]

user_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
