from icecream import ic
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU

other_rt = Router()


@other_rt.message(F.photo)
async def _photo(message: Message):
    await message.reply(text=LEXICON_RU['you_send_a_photo'])


@other_rt.message(F.content_type.in_({'voice', 'video', 'text'}))
async def _process_send_voice_video_text(message: Message):
    await message.answer(text=LEXICON_RU['you_send_voice_text_or_video'])


@other_rt.message(F.location)
async def _localtion(message: Message):
    await message.reply(text=LEXICON_RU['you_send_a_location'])

@other_rt.callback_query(F.data)
async def _other_callback_answer(callback: CallbackQuery):
    await callback.answer(text=f"{LEXICON_RU['unknown_callback']} {callback.data}")


@other_rt.message()
async def _other_messages(message: Message):
    await message.reply(text=LEXICON_RU['bot_not_understanding'])
