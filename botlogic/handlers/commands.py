from aiogram.filters import Command
from aiogram.types import Message
from botlogic.settings import dp


# Хэндлер для команды /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer("Привет!")


# Хэндлер для команды /help
@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    await message.answer("Помощь!")

# Хэндлер для всех прочих текстовых сообщений, не обрабатываемых первыми двумя
# этот хэндлер должен идти последним в списке, иначе будет ловить все апдейты
@dp.message()
async def other_messages(message: Message):
    await message.answer(message.text)
