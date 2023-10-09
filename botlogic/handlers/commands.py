
from aiogram import types, Router, html
from aiogram.filters import Command, CommandObject
from aiogram.enums.dice_emoji import DiceEmoji
from botlogic.settings import Secrets

from botlogic.settings import dp, bot

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, <b>world</b>!", parse_mode="HTML")
    await message.answer("Hello, *world*\!", parse_mode="MarkdownV2")


@router.message(Command("name"))
async def cmd_name(message: types.Message, command: CommandObject):
    if command.args:
        await message.answer(f"Привет, {html.bold(html.quote(command.args))}")
    else:
        await message.answer("Пожалуйста. укажи свое имя после команды /name!")


#TODO: Необходимо получить значение выпавшее на кубике
@router.message(Command("dice"))
async def cmd_dice(message: types.Message):
    #await message.answer_dice(emoji="🎲")
    await bot.send_dice(message.chat.id, emoji=DiceEmoji.DICE)


# Хэндлер для команды stop с проверкой вызывающего id по списку админов
@router.message(Command("stop"))
async def cmd_stop(message: types.Message):
    admins = Secrets.admin_id.split(",")
    for admin in admins:
        if int(admin) != message.from_user.id:
            await message.answer("Gone!")
        else:
            await dp.stop_polling()
            await bot.session.close()
