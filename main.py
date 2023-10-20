import asyncio

from aiogram import Bot, Dispatcher

from handlers import new_user_handlers, admin_handlers, other_handlers, known_users
from settings import BotSecrets

bot = Bot(token=BotSecrets.bot_token, parse_mode="HTML")
dp = Dispatcher()


async def start() -> None:
    # Регистрируем роутеры в диспетчере
    dp.include_router(new_user_handlers.new_user_rt)
    dp.include_router(admin_handlers.admin_rt)
    dp.include_router(known_users.user_rt)
    dp.include_router(other_handlers.other_rt)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
