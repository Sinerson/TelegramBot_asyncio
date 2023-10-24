from db.sybase import DbConnection
from db.sql_queries import get_abonent_by_phonenumber


# Делаем запрос в БД
def get_abonents_from_db(phone: str) -> list:
    result = DbConnection.execute_query(get_abonent_by_phonenumber, phone)
    return result
