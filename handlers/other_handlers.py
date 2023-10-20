from aiogram import Router
from aiogram.types import Message

other_rt = Router()

# Хэндлер для всех прочих сообщений, не обрабатываемых первыми двумя (/start, /help)
# этот хэндлер должен идти последним в списке, иначе будет ловить все апдейты
@other_rt.message()
async def other_messages(message: Message):
    await message.reply(text="Извините, это сообщение пока не может быть распознано ботом")

