import asyncio
import datetime
import logging

from icecream import ic
from redis.asyncio import Redis

from db.sql_queries import last_payment_query, pay_time_query
# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from settings import DbSecrets


async def add_payments_to_redis(wait_for):
    # print("Вызвали корутину добавления платежей")
    """ Вносит записи о платежах в Redis """
    # global delta
    while True:
        # print(F"Время {datetime.datetime.now()}, проверяем платежи")
        await asyncio.sleep(wait_for)
        # from datetime import datetime
        # logging.error(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Процесс поиска и добавления оплат запущен")
        conn_pays_add = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              decode_responses=DbSecrets.redis_decode)
        result = DbConnection.execute_query(last_payment_query)
        if result:
            for dct in result:
                # Перед внесением платежа, проверим, что этот платеж еще не был обработан,
                # для этого сравним
                #           дату отправки из SV..TBP_TELEGRAM_BOT
                pay_time_for_user_id = DbConnection.execute_query(pay_time_query, (int(dct['USER_ID']),))[0][
                    'send_time']
                #           и дату платежа в INT_PAYM
                new_pay_date = dct['PAY_DATE']
                if pay_time_for_user_id and new_pay_date:
                    # Если уже существует такой ключ - пропускаем
                    # print("Такой платеж уже есть")
                    if await conn_pays_add.exists(f"{dct['USER_ID']}:{dct['PAY_DATE'].strftime('%Y:%m:%d:%H:%M:%S')}"):
                        # logging.error("Key is present, pass")
                        continue
                    # Если выборка из базы старее чем уже отправленные - пропускаем:
                    elif new_pay_date <= pay_time_for_user_id:
                        # print("Не прошло сравнение времени предыдщей отправки и нового платежа")
                        # logging.error("Payment is old, pass")
                        continue
                    else:
                        # Иначе, добавляем в redis для отправки
                        # print(f"Время {datetime.datetime.now()}, обнаружили платежные данные")
                        logging.info(
                            f"Поставили в очередь на отправку уведомление для user_id: {dct['USER_ID']} сумму {dct['PAY_MONEY']} руб., дата платежа: {dct['PAY_DATE']} ")
                        await conn_pays_add.lpush(f"{dct['USER_ID']}:{dct['PAY_DATE'].strftime('%Y:%m:%d:%H:%M:%S')}",
                                                  str(dct['PAY_MONEY']))
                else:
                    continue
