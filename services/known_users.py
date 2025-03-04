# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from db.sql_queries import get_known_user_query
from icecream import ic


def get_known_users() -> list[int]:
    result = DbConnection.execute_query(get_known_user_query)
    known_user_ids = []
    for el in result:
        known_user_ids.append(list(el.values())[0])
    return list(map(int, known_user_ids))
