from icecream import ic
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.state import default_state
from services.yagpt_generator import generate_answer
from services.classes import Abonent

#
other_rt = Router()


@other_rt.message(F.photo)
async def _photo(message: Message):
    await message.reply(text=LEXICON_RU['you_send_a_photo'])


@other_rt.message(F.content_type.in_({'voice', 'video', 'text'}), ~StateFilter(default_state))
async def _fsm_process_send_voice_video_text(message: Message):
    await message.answer(text=LEXICON_RU['return_to_FSM'])


@other_rt.message(F.content_type.in_({'text'}), StateFilter(default_state))
async def _process_send_voice_video(message: Message):
    user_id = message.from_user.id
    abonent = Abonent(user_id=user_id)
    await abonent.load_data()

    result = await generate_answer(
        user_message=message.text,
        user_id=user_id,
        abonent=abonent
    )
    await message.answer(text=result)
    abonent.is_first_message = False


@other_rt.message(F.content_type.in_({'voice', 'video'}), StateFilter(default_state))
async def _process_send_voice_video(message: Message):
    await message.answer(text=LEXICON_RU['you_send_voice_or_video'])


@other_rt.message(F.location)
async def _localtion(message: Message):
    await message.reply(text=LEXICON_RU['you_send_a_location'])


@other_rt.callback_query(F.data)
async def _other_callback_answer(callback: CallbackQuery):
    await callback.answer(text=f"{LEXICON_RU['unknown_callback']} {callback.data}")


@other_rt.message(StateFilter(default_state))
async def _other_messages(message: Message):
    await message.reply(text=LEXICON_RU['bot_not_understanding'])

