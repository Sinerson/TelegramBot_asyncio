from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Послать сообщение пользователям бота")],
    [KeyboardButton(text="Проверка связи с БД", request_contact=True)],
    [KeyboardButton(text="Добавить менеджера"), KeyboardButton(text="Добавить админа")],
    [KeyboardButton(text="Мой баланс"), KeyboardButton(text="Мои услуги")]
]

admin_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
