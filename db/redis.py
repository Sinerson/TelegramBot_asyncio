import redis
from settings import DbSecrets


class RedisConnector(object):
    def __init__(self):
        self.host = DbSecrets.redis_host
        self.port = DbSecrets.redis_port
        self.db = DbSecrets.redis_db
        self.decode_responses = DbSecrets.redis_decode
        self.charset = DbSecrets.redis_charset

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
