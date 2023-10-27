from db.sybase import DbConnection
from db.sql_queries import get_user_query


def get_known_users() -> list[int]:
    result = DbConnection.execute_query(get_user_query)
    known_user_ids = []
    for el in result:
        known_user_ids.append(list(el.values())[0])
    return list(map(int, known_user_ids))
