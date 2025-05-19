import asyncio
import datetime
import logging

from icecream import ic
from redis.asyncio import Redis

from db.sql_queries import last_payment_query, pay_time_query, new_last_payment_query
# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from settings import DbSecrets


async def get_last_payment_id() -> int:
    r = Redis(host='192.168.9.184', port=6379, db=3, decode_responses=True, encoding='utf-8')
    last_pay_id = await r.get('last_pay_id')
    await r.aclose()
    return last_pay_id


async def push_payment_data(*args) -> None:
    r = Redis(host='192.168.9.184', port=6379, db=3, decode_responses=True, encoding='utf-8')
    k, v, id = args
    await r.lpush(k, v)
    await r.set('last_pay_id', id)
    await r.aclose()


async def add_payments_to_redis(wait_for):
    # print("Вызвали корутину добавления платежей")
    """ Вносит записи о платежах в Redis """
    # global delta
    while True:
        # print(F"Время {datetime.datetime.now()}, проверяем платежи")
        await asyncio.sleep(wait_for)
        # получим текущее значение PAY_ID
        lpid = await get_last_payment_id()
        # print(f"максимальный PAY_ID: {lpid}")
        # Выберем top 50 платежей
        try:
            paym_list = DbConnection.execute_query(new_last_payment_query, (167418032 if lpid is None else int(lpid),))
            if len(paym_list) > 0:
                for pay in paym_list:
                    last = await get_last_payment_id()
                    if pay['PAY_ID'] > 167418032 if last is None else last:
                        print(f"Время {datetime.datetime.now()}, обнаружили платежные данные")
                        logging.info(
                            f"Поставили в очередь на отправку уведомление для user_id: {pay['USER_ID']} сумму {pay['PAY_MONEY']} руб., дата платежа: {pay['PAY_DATE']}, ID платежа: {int(pay['PAY_ID'])} ")
                        await push_payment_data(f"{pay['USER_ID']}:{pay['PAY_DATE'].strftime('%Y:%m:%d:%H:%M:%S')}",
                                                str(pay['PAY_MONEY']), int(pay['PAY_ID']))
                    else:
                        print(f"PAY_ID: {pay['PAY_ID']} меньше чем {last}")
                        continue
            else:
                continue
        except Exception as e:
            logging.error(f"Не получилось достучаться до базы или добавить в Redis платеж. Ошибка: {e}")
            continue
