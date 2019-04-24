# -*- coding: utf-8 -*-
import redis

import settings


class RedisClient(object):
    _client = None

    def __init__(self):
        if self._client is None:
            self._create_redis_client()

    @classmethod
    def _create_redis_client(cls):
        """
        创建连接
        :return:
        """
        # not to use the connection pooling when using the redis-py client in Tornado applications
        # http://stackoverflow.com/questions/5953786/how-do-you-properly-query-redis-from-tornado/15596969#15596969
        # 注意这里必须是 settings.REDIS_HOST
        # 否则在 runserver 中若修改了 settings.REDIS_HOST，这里就不能生效
        RedisClient._client = redis.StrictRedis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT,
            db=settings.REDIS_DB, password=settings.REDIS_PASS)

    @classmethod
    def get_client(cls):
        if RedisClient._client is None:
            cls._create_redis_client()
        return RedisClient._client
