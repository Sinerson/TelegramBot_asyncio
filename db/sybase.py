import pyodbc
from settings import DbSecrets
from icecream import ic


class DBConnector(object):
    def __init__(self):
        self.driver = DbSecrets.driver
        self.server = DbSecrets.server
        self.port = DbSecrets.port
        self.dbname = DbSecrets.db_name
        self.user = DbSecrets.user
        self.passw = DbSecrets.password
        self.lang = DbSecrets.lang
        self.autocommit = DbSecrets.autocommit
        self.hostname = DbSecrets.hostname
        self.procname = DbSecrets.proc_name
        self.appname = DbSecrets.app_name

    def create_connection(self):
        return pyodbc.connect(';'.join([self.driver, self.server, self.port, self.dbname, self.user, self.passw,
                                        self.lang, self.autocommit, self.hostname, self.procname, self.appname]))

    def __enter__(self):
        self.dbconn = self.create_connection()
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()


class DbConnection(object):
    connection = None

    @classmethod
    def get_connection(cls, new=False):
        if new or not cls.connection:
            cls.connection = DBConnector().create_connection()
            cls.connection.autocommit = True  # принудительный автокоммит, т.к. он почему-то игнорится в строке подключения
        return cls.connection

    @classmethod
    def execute_query(cls, query, params=None) -> list:
        connection = cls.get_connection()
        result = []
        try:
            cursor = connection.cursor()
        except pyodbc.ProgrammingError:
            connection = cls.get_connection(new=True)
            cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        for row in cursor.fetchall():
            columns = [column[0] for column in cursor.description]
            result.append(dict(zip(columns, row)))
        cursor.close()
        return result
