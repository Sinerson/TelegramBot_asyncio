import asyncio
import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import Redis, RedisStorage
# from aiogram.fsm.storage.memory import MemoryStorage
import logging
from handlers import new_user_handlers, admin_handlers, other_handlers, known_users_handlers, ban_unban_handler, \
                     poll_handler
from services.other_functions import check_ban_by_user
from services.payments_processing_to_redis import add_payments_to_redis
from services.send_payment_notice import send_payment_notice
from settings import BotSecrets, DbSecrets

logging.basicConfig(level=logging.DEBUG,
                    filename="log\\Log.txt",
                    filemode="a",
                    format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                    )

# Инициализируем Redis
redis = Redis(host=DbSecrets.redis_host, port=DbSecrets.redis_port, db=0)

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
# storage = MemoryStorage()
# 1 вариант подключения
# storage = RedisStorage.from_url('redis://localhost:6379/0')
# 2 вариант подключения
storage = RedisStorage(redis=redis)

bot = Bot(token=BotSecrets.bot_token, default=DefaultBotProperties(parse_mode="HTML"))

dp = Dispatcher(storage=storage)


async def start() -> None:
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Запуск бота.")
    # Регистрируем роутеры в диспетчере
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Регистрация диспетчеров")
    dp.include_router(ban_unban_handler.ban_rt)
    dp.include_router(poll_handler.poll_rt)
    dp.include_router(new_user_handlers.new_user_rt)
    dp.include_router(admin_handlers.admin_rt)
    dp.include_router(known_users_handlers.user_rt)
    dp.include_router(other_handlers.other_rt)

    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Пропуск всех накопленных апдейтов")
    await bot.delete_webhook(drop_pending_updates=True)
    # logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Создание планировщика")
    #   Планировщик
    loop = asyncio.get_event_loop()
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} постановка в планировщик задачи добавления платежей")
    #   добавление оплат в redis
    loop.create_task(add_payments_to_redis(35))
    #   отправка уведомления пользователю
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} постановка в планировщик задачи отправки уведомления о платежах")
    loop.create_task(send_payment_notice(20))
    # Проверка у кого из пользователей бот забанен
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} постановка в планировщик задачи проверки забанивших бота")
    loop.create_task(check_ban_by_user(10800))
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Запуск основного тела бота")
    await dp.start_polling(bot)


async def stop() -> None:
    await bot.session.close()
    logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Бот закрыт")


if __name__ == '__main__':
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    try:
        asyncio.set_event_loop_policy(policy)
        asyncio.run(start())#, debug=True)
    except KeyboardInterrupt:
        logging.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Исключение прервания с клавиатуры")
        asyncio.run(stop())
    except RuntimeError:
        logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Бот закрыт")
    except OSError:
        logging.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Возникла OSError")
