import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter
from icecream import ic
from redis.asyncio import Redis

from lexicon.lexicon_ru import LEXICON_RU
from services.other_functions import user_banned_bot_processing
from settings import BotSecrets, DbSecrets
# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from db.sql_queries import set_payment_notice_status
from datetime import datetime, timedelta

bot = Bot(token=BotSecrets.bot_token,
          default=DefaultBotProperties(parse_mode='HTML'),
          )


async def send_payment_notice(delay_timer):
    """ Функция отправки уведомления о поступившем платеже """
    while True:
        await asyncio.sleep(delay_timer)
        # logging.error(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Процесс отправки запущен")
        conn_pays_get = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              decode_responses=DbSecrets.redis_decode)
        for el in await conn_pays_get.keys():
            if len(el.split(':')) > 1:
                tg_user_id = int(el.split(':')[1])
                pay_date = (f"{el.split(':')[2]}-"
                            f"{el.split(':')[3]}-"
                            f"{el.split(':')[4]} "
                            f"{el.split(':')[5]}:"
                            f"{el.split(':')[6]}:"
                            f"{el.split(':')[7]}")
                pay_sum = await conn_pays_get.lpop(el)
                try:
                    result = DbConnection.execute_query(set_payment_notice_status,
                                                        (pay_date, float(pay_sum), tg_user_id))
                    logging.info(
                        f"Результат обновления даты последнего платежа для пользователя {tg_user_id}: {'Успех' if result[0]['UPDATE_RESULT'] == 1 else 'Неудача'}")
                    res = await bot.send_message(chat_id=124902528,  # tg_user_id,
                                                 text=f"{LEXICON_RU['get_payment']} {round(float(pay_sum), 2)} {LEXICON_RU['rubles']}\n",
                                                 disable_notification=True)
                    if res.message_id:
                        logging.info(
                            f"Уведомление о платеже на сумму: {round(float(pay_sum), 2)} пользователю {tg_user_id} ({res.chat.username} {res.chat.first_name}) успешно отправлено в {res.date}")
                        await asyncio.sleep(0.2)
                    else:
                        logging.error(f"Не удалось отправить сообщение об оплате пользователю {tg_user_id}")
                        continue
                except TelegramForbiddenError:
                    logging.error(f"Похоже пользователь {tg_user_id} нас забанил, отметим в базе этого неудачника")
                    user_banned_bot_processing(tg_user_id)
                    continue
                except TelegramBadRequest:
                    logging.error("Не удалось отправить запрос к серверам телеграм")
                    continue
                except TelegramRetryAfter:
                    logging.error(f"Слишком часто посылаем сообщения. Сервер Telegram ругается. Засыпаем на 3 секунды")
                    await asyncio.sleep(3)
                    continue

            else:
                continue
