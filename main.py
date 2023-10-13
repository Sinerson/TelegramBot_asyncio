import asyncio

from botlogic.handlers.events import start_bot, stop_bot
from botlogic.settings import bot, dp
from botlogic.settings import Secrets, router
from botlogic.handlers.commands import cmd_start, cmd_help, other_messages, bot_banned, bot_unbanned,\
     process_if_numbers, process_if_not_numbers


async def start():
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(router)
    dp.message.register(cmd_start, cmd_help, other_messages, bot_banned, bot_unbanned,
                        process_if_numbers, process_if_not_numbers)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # TODO: Разобраться как забирать в других хэндлерах переданные в polling списки admin_list и manager_list
        await dp.start_polling(bot, admin_list=Secrets.admin_id, manager_list=Secrets.manager_id)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
