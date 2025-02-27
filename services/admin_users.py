from icecream import ic

# from db.sybase import DbConnection
from db.sybase import DbConnectionHandler as DbConnection
from db.sql_queries import get_abonent_by_phonenumber_query, getBalance_query, get_admin_query, get_manager_query


def get_admins() -> list:
    result = DbConnection.execute_query(get_admin_query)
    admin_ids = []
    for el in result:
        admin_ids.append(list(el.values())[0])
    return list(map(int, admin_ids))


def get_manager() -> list:
    result = DbConnection.execute_query(get_manager_query)
    manager_ids = []
    for el in result:
        manager_ids.append(list(el.values())[0])
    return list(map(int, manager_ids))
