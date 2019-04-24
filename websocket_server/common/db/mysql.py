# -*- coding: utf-8 -*-
import logging
import time
import decimal
from datetime import datetime

import pymysql
from tornado_mysql import pools
from tornado_mysql.cursors import DictCursor

import settings

logger = logging.getLogger(__name__)


class MyDictCursorMix(object):
    def _conv_row(self, row):
        def translate_type(value):
            if isinstance(value, datetime):
                return time.mktime(value.timetuple())
            elif isinstance(value, decimal.Decimal):
                return float(value)
            else:
                return value

        if row is None:
            return None
        return self.dict_type(zip(self._fields, map(translate_type, row)))


class MyDictCursor(MyDictCursorMix, DictCursor):
    """自定义Cursor,对于数据库直接获得的数据,无法序列化的转换"""


class MySQLPOOL(object):
    _pool = None

    def __init__(self):
        if MySQLPOOL._pool is None:
            self._create_mysql_pool()

    @classmethod
    def get_pool(cls):
        if MySQLPOOL._pool is None:
            cls._create_mysql_pool()

        return MySQLPOOL._pool

    @classmethod
    def _create_mysql_pool(cls):
        MySQLPOOL._pool = pools.Pool(
            dict(host=settings.MYSQL_DB_HOST,
                 port=settings.MYSQL_DB_PORT,
                 user=settings.MYSQL_DB_USER,
                 passwd=settings.MYSQL_DB_PASSWORD,
                 db=settings.MYSQL_DB_DBNAME,
                 cursorclass=MyDictCursor,
                 charset=settings.MYSQL_CHARSET
                 ),
            max_recycle_sec=settings.MYSQL_MAX_RECYCLE_SEC,
            max_idle_connections=settings.MYSQL_IDLE_CONNECTIONS
        )


def get_connection(host=settings.MYSQL_DB_HOST,
                   port=settings.MYSQL_DB_PORT,
                   user=settings.MYSQL_DB_USER,
                   password=settings.MYSQL_DB_PASSWORD,
                   charset=settings.MYSQL_CHARSET,
                   db=settings.MYSQL_DB_DBNAME,
                   autocommit=False, ):
    conn = None
    try:
        conn = pymysql.connect(
            host=host, port=port,
            user=user, password=password,
            db=db, charset=charset,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=autocommit
        )
    except:
        logger.exception("get connection error")
    return conn
