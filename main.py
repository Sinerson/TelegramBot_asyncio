import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import new_user_handlers, admin_handlers, other_handlers, known_users_handlers, ban_unban_handler, \
                     poll_handler
from services.other_functions import add_payments_to_redis, send_payment_notice
from settings import BotSecrets, DbSecrets

# Инициализируем Redis
redis = Redis(host=DbSecrets.redis_host, port=DbSecrets.redis_port, db=0)

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
# storage = MemoryStorage()
# 1 вариант подключения
# storage = RedisStorage.from_url('redis://localhost:6379/0')
# 2 вариант подключения
storage = RedisStorage(redis=redis)

bot = Bot(token=BotSecrets.bot_token, parse_mode="HTML")

dp = Dispatcher(storage=storage)


async def start() -> None:
    # Регистрируем роутеры в диспетчере
    dp.include_router(ban_unban_handler.ban_rt)
    dp.include_router(poll_handler.poll_rt)
    dp.include_router(new_user_handlers.new_user_rt)
    dp.include_router(admin_handlers.admin_rt)
    dp.include_router(known_users_handlers.user_rt)
    dp.include_router(other_handlers.other_rt)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # Планировщик
        loop = asyncio.get_event_loop()
        #     добавление оплат в redis
        loop.create_task(add_payments_to_redis(31))
        #     отправка уведомления пользователю
        loop.create_task(send_payment_notice(10))
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
