from db.sybase import DbConnection
from db.sql_queries import get_abonent_by_phonenumber

# Делаем запрос в БД
async def get_abonents_from_db(phone: str) -> list:
    result = DbConnection.execute_query(phone)
    return result
