import redis


class RedisConnector(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 6379
        self.db = 1
        self.decode_responses = True
        self.charset = 'utf-8'

    def create_connection(self, database=None):
        if database is None:
            database = self.db
        return redis.Redis(host=self.host,
                           port=self.port,
                           db=database,
                           decode_responses=self.decode_responses,
                           charset=self.charset
                           )

    def __enter__(self):
        self.dbconn = self.create_connection()
        return self.dbconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbconn.close()
