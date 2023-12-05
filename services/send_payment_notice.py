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
        print("Процесс отправки запущен")
        conn_pays_get = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              charset=DbSecrets.redis_charset,
                              decode_responses=DbSecrets.redis_decode)
        for el in conn_pays_get.keys():
            now_datetime = datetime.now()
            payment = DbConnection.execute_query(pay_time_query, int(el))[0]
            delta = now_datetime - payment['send_time']
            tg_user_id = int(el)
            pay_sum_redis = float(conn_pays_get.lpop(el))
            pay_sum_sybase = float(payment['paid_money'])
            if delta.seconds <= 60 and pay_sum_sybase == pay_sum_redis:
                pass
            else:
                DbConnection.execute_query(set_payment_notice_status, float(pay_sum_redis), tg_user_id)
                await bot.send_message(chat_id=tg_user_id,
                                       text=f"{LEXICON_RU['get_payment']} {round(float(pay_sum_redis), 2)} {LEXICON_RU['rubles']} \n",
                                       disable_notification=False)
