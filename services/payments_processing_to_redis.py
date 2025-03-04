import asyncio
import logging

from icecream import ic
from redis import Redis

from db.sql_queries import last_payment_query, pay_time_query
# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from settings import DbSecrets


async def add_payments_to_redis(wait_for):
    """ Вносит записи о платежах в Redis """
    global delta
    while True:
        await asyncio.sleep(wait_for)
        from datetime import datetime
        # logging.error(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Процесс поиска и добавления оплат запущен")
        conn_pays_add = Redis(host=DbSecrets.redis_host,
                              port=DbSecrets.redis_port,
                              db=3,
                              encoding='utf-8',
                              charset=DbSecrets.redis_charset,
                              decode_responses=DbSecrets.redis_decode)
        result = DbConnection.execute_query(last_payment_query)
        if result:
            for dict in result:
                # Перед внесением платежа, проверим, что этот платеж еще не был обработан,
                # для этого сравним
                #           дату отправки из SV..TBP_TELEGRAM_BOT
                pay_time_for_user_id = DbConnection.execute_query(pay_time_query, int(dict['USER_ID']))[0]['send_time']
                #           и дату платежа в INT_PAYM
                new_pay_date = dict['PAY_DATE']
                if pay_time_for_user_id and new_pay_date:
                    # Если уже существует такой ключ - пропускаем
                    if conn_pays_add.exists(f"{dict['USER_ID']}:{dict['PAY_DATE'].strftime('%Y:%m:%d:%H:%M:%S')}"):
                        # logging.error("Key is present, pass")
                        pass
                    # Если выборка из базы старее чем уже отправленные - пропускаем:
                    elif new_pay_date <= pay_time_for_user_id:
                        # logging.error("Payment is old, pass")
                        pass
                    else:
                        # Иначе, добавляем в redis для отправки
                        conn_pays_add.lpush(f"{dict['USER_ID']}:{dict['PAY_DATE'].strftime('%Y:%m:%d:%H:%M:%S')}",
                                                  str(dict['PAY_MONEY']))
                        logging.info(f"Поставили в очередь на отправку уведомления для user_id: {dict['USER_ID']} сумму {dict['PAY_MONEY']} руб., дата платежа: {dict['PAY_DATE']} ")
                else:
                    pass
