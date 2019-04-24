# -*- coding: utf-8 -*-
import logging

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

logger = logging.getLogger(__name__)


class BaseRequestHandler(RequestHandler):
    def success(self, msg, data=None):
        """
        执行成功,code为200,msg信息为实际信息,data存在时,将data一并返回
        :param msg:
        :param data:
        :return:
        """
        result = {
            "code": 200,
            "message": msg
        }
        if data is not None:
            result['data'] = data
        self.finish(result)

    def fail(self, msg, code=400, data=None):
        result = {
            "code": int(code),
            "message": msg
        }
        if data is not None:
            result['data'] = data
        self.finish(result)

    @property
    def db(self):
        return self.application.db.get_pool()

    @property
    def redis(self):
        return self.application.redis.get_client()

class BaseWebsocketHandler(BaseRequestHandler, WebSocketHandler):
    def fail(self, msg, code=400, data=None):
        result = {
            "code": int(code),
            "message": msg
        }
        if data is not None:
            result['data'] = data
        self.set_status(code, msg)
        self.finish(result)
