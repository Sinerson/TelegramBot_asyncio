from aiogram import Router, F
from aiogram.types import Message

other_rt = Router()


# Хэндлер для всех прочих сообщений, не обрабатываемых первыми двумя (/start, /help)
# этот хэндлер должен идти последним в списке, иначе будет ловить все апдейты

@other_rt.message(F.photo)
async def _photo(message: Message):
    await message.reply(text="Вы прислали фото")


@other_rt.message(F.content_type.in_({'voice', 'video', 'text'}))
async def process_send_vovite(message: Message):
    await message.answer(text='Вы прислали войс, видео или текст')


@other_rt.message(F.location)
async def _photo(message: Message):
    await message.reply(text="Вы прислали геопозицию")


@other_rt.message()
async def _other_messages(message: Message):
    await message.reply(text="Извините, это сообщение пока не может быть распознано ботом")
