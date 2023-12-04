import asyncio

from aiogram import Bot
from icecream import ic
from redis import Redis

from lexicon.lexicon_ru import LEXICON_RU
from settings import BotSecrets, DbSecrets

bot = Bot(token=BotSecrets.bot_token, parse_mode="HTML")


async def send_payment_notice(delay_timer):
    """ Функция отправки уведомления о поступившем платеже """
    while True:
        await asyncio.sleep(delay_timer)
        conn_pays_get = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              charset=DbSecrets.redis_charset,
                              decode_responses=DbSecrets.redis_decode)
        keys = conn_pays_get.keys()
        for el in keys:
            pay_sum = conn_pays_get.lpop(el)
            await bot.send_message(chat_id=124902528,
                                   text=f"{LEXICON_RU['get_payment']} {round(float(pay_sum), 2)} {LEXICON_RU['rubles']}")
