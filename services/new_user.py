from db.sybase import DbConnection
from db.sql_queries import checkUserExists
from icecream import ic


def userIsExist(user_id: str) -> int:
    result = DbConnection.execute_query(checkUserExists, user_id)
    ic(max(int, result))
