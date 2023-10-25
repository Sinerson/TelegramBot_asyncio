from db.sybase import DbConnection
from db.sql_queries import get_user_query


def get_known_users() -> list[int]:
    result = DbConnection.execute_query(get_user_query)
    manager_ids = []
    for el in result:
        manager_ids.append(list(el.values())[0])
    return list(map(int, manager_ids))
