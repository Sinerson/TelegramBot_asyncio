from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

# ----------------------------------- Кнопка отправки контакта ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text="Послать сообщение пользователям бота")],
    [KeyboardButton(text="Статистика по боту")],
    [KeyboardButton(text="Добавить менеджера")],
    [KeyboardButton(text="Добавить админа")]
]

admin_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
