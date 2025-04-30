from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon_ru import LEXICON_RU
from icecream import ic
import copy

# ----------------------------------- Меню кнопок для пользователей ----------------------------------------------
# Создаем список списков с кнопками
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text=LEXICON_RU['my_balance']), KeyboardButton(text=LEXICON_RU['my_services'])]
    , [KeyboardButton(text=LEXICON_RU['new_services_request']), KeyboardButton(text=LEXICON_RU['promised_payment'])]
    , [KeyboardButton(text=LEXICON_RU['inet_password']), KeyboardButton(text=LEXICON_RU['personal_area_password'])]
    # , [KeyboardButton(text=LEXICON_RU['drop_the_dice'])],
    # KeyboardButton(text=LEXICON_RU['take_part_in_the_survey'])
    , [KeyboardButton(text=LEXICON_RU['my_support_tickets']), ]
]

user_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def without_dice_kb_known_users() -> ReplyKeyboardMarkup:
    now_buttons = copy.copy(buttons)
    now_buttons.pop(3)
    return ReplyKeyboardMarkup(keyboard=now_buttons, resize_keyboard=True)


def survey_list_kb(surveys: list) -> InlineKeyboardMarkup:
    surveys_list = []
    for el in surveys:
        survey_button = [
            InlineKeyboardButton(text=f"{el['SURVEY_SHORT_NAME']}", callback_data=f"SURVEY_CHOOSE {el['SURVEY_ID']} {el['TYPE_ID']}")]
        surveys_list.append(survey_button)
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=surveys_list)


def survey_grade_choose(survey_id: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="1", callback_data=f"SURVEY_GRADE {survey_id} 1"),
         InlineKeyboardButton(text="2", callback_data=f"SURVEY_GRADE {survey_id} 2"),
         InlineKeyboardButton(text="3", callback_data=f"SURVEY_GRADE {survey_id} 3"),
         InlineKeyboardButton(text="4", callback_data=f"SURVEY_GRADE {survey_id} 4"),
         InlineKeyboardButton(text="5", callback_data=f"SURVEY_GRADE {survey_id} 5")],
        [InlineKeyboardButton(text="6", callback_data=f"SURVEY_GRADE {survey_id} 6"),
         InlineKeyboardButton(text="6", callback_data=f"SURVEY_GRADE {survey_id} 7"),
         InlineKeyboardButton(text="8", callback_data=f"SURVEY_GRADE {survey_id} 8"),
         InlineKeyboardButton(text="9", callback_data=f"SURVEY_GRADE {survey_id} 9"),
         InlineKeyboardButton(text="10", callback_data=f"SURVEY_GRADE {survey_id} 10")],
    ]
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)
