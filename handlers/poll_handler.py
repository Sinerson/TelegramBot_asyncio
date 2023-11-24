from aiogram import Router
from aiogram.types import Message
from icecream import ic

poll_rt = Router()


# Хэндлер для апдейтов на ответы в голосовании
@poll_rt.poll_answer()
async def _get_poll_answer(message: Message):
    ic(message)
    ic(message.user.id)
    ic(message.user.first_name)
    ic(message.poll_id)
    ic(message.option_ids)
