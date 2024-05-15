from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
import copy

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup
from icecream import ic

from lexicon.lexicon_ru import LEXICON_RU

# Создаем список списков с кнопками для основного меню
buttons: list[list[KeyboardButton]] = [
    [KeyboardButton(text=LEXICON_RU['make_a_spam']), KeyboardButton(text=LEXICON_RU['drop_the_dice'])]
    , [KeyboardButton(text=LEXICON_RU['make_poll']), KeyboardButton(text=LEXICON_RU['get_poll_result'])]
    # , [KeyboardButton(text=LEXICON_RU['del_manager']), KeyboardButton(text=LEXICON_RU['del_admin'])]
    , [KeyboardButton(text=LEXICON_RU['add_manager']), KeyboardButton(text=LEXICON_RU['add_admin'])]
    , [KeyboardButton(text=LEXICON_RU['my_balance']), KeyboardButton(text=LEXICON_RU['my_services'])]
    , [KeyboardButton(text=LEXICON_RU['inet_password']), KeyboardButton(text=LEXICON_RU['personal_area_password'])]
    , [KeyboardButton(text=LEXICON_RU['promised_payment']), KeyboardButton(text=LEXICON_RU['my_support_tickets'])]
    , [KeyboardButton(text=LEXICON_RU['take_part_in_the_survey'])]
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


def keyboard_with_contract_client_type_code(abonents_data: list[dict], callback_name: str) -> InlineKeyboardMarkup:
    button_list = []
    for dicts in abonents_data:
        button = []
        button.append(InlineKeyboardButton(text=f"{LEXICON_RU['contract']} {str(dicts['CONTRACT'])},"
                                                f" {LEXICON_RU['address']} {str(dicts['ADDRESS'])}",
                                           callback_data=f'{callback_name} {str(dicts["CONTRACT_CODE"])},'
                                                         f' {str(dicts["CLIENT_CODE"])}, {str(dicts["TYPE_CODE"])}'))
        button_list.append(button)
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=button_list)


def yes_no_keyboard(dice_value: int) -> InlineKeyboardMarkup:
    yes_no_buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=LEXICON_RU['yes'], callback_data=f'DICE yes {dice_value}')],
        [InlineKeyboardButton(text=LEXICON_RU['no'], callback_data=f'DICE no')]
    ]
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=yes_no_buttons)


def without_dice_kb() -> ReplyKeyboardMarkup:
    now_buttons = copy.copy(buttons)
    now_buttons[0].pop(1)
    return ReplyKeyboardMarkup(keyboard=now_buttons, resize_keyboard=True)


def stop_spam_kb(user_id: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=LEXICON_RU['stop_spam'], callback_data=f"STOP_SPAM {user_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_poll_list(polls: dict) -> InlineKeyboardMarkup:
    button_list = []
    for el in polls:
        button = [InlineKeyboardButton(text=f"{polls[el]}", callback_data=f'P_STAT {el}')]
        button_list.append(button)
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=button_list)


def survey_list_kb(surveys: list) -> InlineKeyboardMarkup:
    surveys_list = []
    for el in surveys:
        survey_button = [InlineKeyboardButton(text=f"{el['SURVEY_SHORT_NAME']}", callback_data=f"SURVEY_CHOOSE {el['SURVEY_ID']}")]
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
