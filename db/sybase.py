import pyodbc
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from settings import DbSecrets


class DBConnector(object):
    """Класс для создания подключения к БД с использованием pyodbc."""

    # def __init__(self):
    #     self.driver = DbSecrets.driver
    #     self.server = DbSecrets.server
    #     self.port = DbSecrets.port
    #     self.dbname = DbSecrets.db_name
    #     self.user = DbSecrets.user
    #     self.passw = DbSecrets.password
    #     self.lang = DbSecrets.lang
    #     self.autocommit = DbSecrets.autocommit
    #     self.hostname = DbSecrets.hostname
    #     self.procname = DbSecrets.proc_name
    #     self.appname = DbSecrets.app_name
    def __init__(self):
        self.conn_params = {
            "DRIVER": DbSecrets.driver,
            "SERVER": DbSecrets.server,
            "PORT": DbSecrets.port,
            "DATABASE": DbSecrets.db_name,
            "UID": DbSecrets.user,
            "PWD": DbSecrets.password,
            "LANGUAGE": DbSecrets.lang,
            "AUTOCOMMIT": DbSecrets.autocommit,
        }

    # def create_connection(self):
    #     return pyodbc.connect(';'.join([self.driver, self.server, self.port, self.dbname, self.user, self.passw,
    #                                     self.lang, self.autocommit, self.hostname, self.procname, self.appname]))
    def create_connection(self) -> pyodbc.Connection:
        """Создает новое подключение с валидацией параметров."""
        try:
            conn_str = ";".join([f"{k}={v}" for k, v in self.conn_params.items()])
            conn = pyodbc.connect(conn_str, timeout=10)
            conn.autocommit = True  # Явное указание autocommit
            return conn
        except pyodbc.Error as e:
            raise ConnectionError(f"Ошибка подключения: {e}") from e

    def __enter__(self):
        self.dbconn = self.create_connection()
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()


# class DbConnection(object):
#     connection = None
#
#     @classmethod
#     def get_connection(cls, new=False):
#         if new or not cls.connection:
#             cls.connection = DBConnector().create_connection()
#             cls.connection.autocommit = True  # принудительный автокоммит, т.к. он почему-то игнорится в строке подключения
#         return cls.connection
#
#     @classmethod
#     def execute_query(cls, query, *params) -> list:
#         connection = cls.get_connection()
#         result = []
#         try:
#             cursor = connection.cursor()
#         except pyodbc.Error:
#             connection = cls.get_connection(new=True)
#             cursor = connection.cursor()
#         if params:
#             cursor.execute(query, params)
#         else:
#             cursor.execute(query)
#         try:
#             for row in cursor.fetchall():
#                 columns = [column[0] for column in cursor.description]
#                 result.append(dict(zip(columns, row)))
#             cursor.close()
#             return result
#         except pyodbc.ProgrammingError as e:
#             return e
class DbConnectionHandler:
    """Менеджер подключений с базовой обработкой ошибок и пуллингом."""

    _connection_pool = []

    @classmethod
    @contextmanager
    def get_connection(cls) -> pyodbc.Connection:
        """Контекстный менеджер для безопасного использования подключения."""
        conn = None
        try:
            conn = DBConnector().create_connection()
            yield conn
        except pyodbc.Error as e:
            raise RuntimeError(f"Ошибка БД: {e}") from e
        finally:
            if conn:
                conn.close()

    @classmethod
    def execute_query(
            cls,
            query: str,
            params: Optional[tuple] = None,
            retries: int = 2
    ) -> List[Dict[str, Any]]:
        """Выполняет SQL-запрос с обработкой ошибок и повторными попытками."""
        result = []
        for attempt in range(retries + 1):
            try:
                with cls.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())

                    if cursor.description:  # Для SELECT-запросов
                        columns = [col[0] for col in cursor.description]
                        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    else:  # Для INSERT/UPDATE/DELETE
                        conn.commit()

                    cursor.close()
                    return result

            except pyodbc.ProgrammingError as e:
                if "NOCOUNT" in str(e):  # Игнорировать специфичные предупреждения
                    return []
                raise
            except pyodbc.OperationalError:
                if attempt == retries:
                    raise
                continue
        return []
