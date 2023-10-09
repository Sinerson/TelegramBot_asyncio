import asyncio

from aiogram.filters import Command

from botlogic.handlers.events import start_bot, stop_bot
from botlogic.settings import bot, dp
from botlogic.handlers.commands import router, cmd_stop, cmd_dice
from botlogic.settings import Secrets


async def start() -> None:
    dp.include_routers(router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.message.register(cmd_stop, Command("stop"))
    dp.message.register(cmd_dice, Command("dice"))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # TODO: Разобраться как забирать в других хэндлерах переданные в polling списки admin_list и manager_list
        await dp.start_polling(bot, admin_list=Secrets.admin_id, manager_list=Secrets.manager_id)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
