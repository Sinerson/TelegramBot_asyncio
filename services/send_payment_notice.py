import asyncio

from aiogram import Bot
from icecream import ic
from redis import Redis

from lexicon.lexicon_ru import LEXICON_RU
from settings import BotSecrets, DbSecrets
from db.sybase import DbConnection
from db.sql_queries import pay_time_query, set_payment_notice_status
from datetime import datetime

bot = Bot(token=BotSecrets.bot_token, parse_mode="HTML")


async def send_payment_notice(delay_timer):
    """ Функция отправки уведомления о поступившем платеже """
    while True:
        await asyncio.sleep(delay_timer)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Процесс отправки запущен")
        conn_pays_get = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              charset=DbSecrets.redis_charset,
                              decode_responses=DbSecrets.redis_decode)
        for el in conn_pays_get.keys():
            now_datetime = datetime.now()
            # ic(now_datetime)
            payment = DbConnection.execute_query(pay_time_query, int(el))[0]
            # ic(payment)
            delta = now_datetime - payment['send_time']
            # ic(delta)
            tg_user_id = int(el)
            # ic(tg_user_id)
            pay_sum_redis = float(conn_pays_get.lpop(el))
            # ic(pay_sum_redis)
            pay_sum_sybase = float(payment['paid_money'])
            # ic(pay_sum_sybase)
            if delta.seconds <= 60 and pay_sum_sybase == pay_sum_redis:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Прошло менее 60 секунд и суммы равны. Отправку не делаем")
                pass
            else:
                DbConnection.execute_query(set_payment_notice_status, float(pay_sum_redis), tg_user_id)
                await bot.send_message(chat_id=124902528,
                                       text=f"{LEXICON_RU['get_payment']} {round(float(pay_sum_redis), 2)} {LEXICON_RU['rubles']} \n",
                                       disable_notification=False)
