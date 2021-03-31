import redis

from django.conf import settings

from Backend_Api.service_setup import redis_cfg


class RedisSett:
    RED_HOST = redis_cfg.REDIS_HOST
    RED_PORT = redis_cfg.REDIS_PORT
    RED_PASS = redis_cfg.REDIS_PASSWORD
    db = None

    @classmethod
    def get_redis_instance(cls, db):
        redis_data = dict(
            host=cls.RED_HOST, port=cls.RED_PORT, password=cls.RED_PASS, db=db
        )
        redis_instance = redis.StrictRedis(**redis_data)
        return redis_instance
