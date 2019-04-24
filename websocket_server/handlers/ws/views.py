#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: views.py
@time: 2019/1/26 17:08
"""
import logging
from concurrent.futures import ThreadPoolExecutor

import tornado.web
from tornado.concurrent import run_on_executor
from tornado.escape import json_decode
from tornado.gen import coroutine

import settings
from common.rabbitmq import RabbitMQClient
from common.room_handler import rlock
from common.tornado.web import BaseWebsocketHandler, BaseRequestHandler

logger = logging.getLogger(__name__)


class ChatHandler(BaseWebsocketHandler):
    executor = ThreadPoolExecutor()

    def initialize(self, room_handler):
        self.room_handler = room_handler

    @coroutine
    def open(self, *args, **kwargs):
        """
        初始化时，确定用户信息
        """
        # 根据登录后设置的cookie信息获取room和nick信息，并关联wsconn
        self.client_id = self.get_cookie('client_id', 0)
        with rlock:
            result = self.room_handler.add_client(self.client_id, self)

        # 通知同一房间所有人某人加入
        join_data = {
            "type": "join",
            "data": result
        }
        yield self.publish_message(join_data, settings.WEBSOCKET_SEND_EXCHANGE, settings.WEBSOCKET_SEND_EXCHANGE)
        # 房间在线人数列表刷新
        nicks_data = {
            "type": "nicks",
            "data": result
        }
        yield self.publish_message(nicks_data, settings.WEBSOCKET_SEND_EXCHANGE, settings.WEBSOCKET_SEND_EXCHANGE)

    @coroutine
    def on_message(self, message):
        """
        收到发送消息通知
        通知在房间的所有用户
        """
        try:
            msg = json_decode(message)
            e_type = msg.get("type")
            t_data = msg.get("data")
            if e_type == "message":
                client_info = self.room_handler.clients_info.get(self.client_id)
                if client_info:
                    room = client_info['room']
                    nick = client_info['nick']
                    msg = t_data.get("message")
                    event_data = {
                        "type": "send_message",
                        "data": {
                            "room": room,
                            "nick": nick,
                            "msg": msg
                        }
                    }
                    # 改由rabbitmq处理
                    yield self.publish_message(event_data, settings.WEBSOCKET_SEND_EXCHANGE,
                                               settings.WEBSOCKET_SEND_EXCHANGE)
                else:
                    logger.error("收到用户[{}]信息，但本地信息不存在 [{}]".format(self.client_id, self.room_handler.clients_info))
            else:
                logger.warning("暂时不支持的类型 type={}".format(e_type))
        except:
            logger.exception("处理事件失败")

    @coroutine
    def on_close(self):
        result = self.room_handler.remove_client(self.client_id)
        if result:
            # 离开房间
            leave_data = {
                "type": "leave",
                "data": result
            }
            yield self.publish_message(leave_data, settings.WEBSOCKET_SEND_EXCHANGE,
                                       settings.WEBSOCKET_SEND_EXCHANGE)
            # 房间在线人数列表刷新
            nicks_data = {
                "type": "nicks",
                "data": result
            }
            yield self.publish_message(nicks_data, settings.WEBSOCKET_SEND_EXCHANGE,
                                       settings.WEBSOCKET_SEND_EXCHANGE)

    def check_origin(self, origin):
        """
        校验来源
        :param origin:
        :return:
        """
        return True

    @run_on_executor
    def publish_message(self, data, exchange_name, routing_key):
        rmq_client = RabbitMQClient()
        rmq_client.publish_message(data, exchange_name, routing_key, exchange_type='direct')


class MainHandler(BaseRequestHandler):
    def initialize(self, room_handler):
        self.room_handler = room_handler

    def get(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        try:
            #: 房间名字
            room = self.get_argument('room')
            #: 用户名字
            nick = self.get_argument('nick')
            #: 指定房间添加指定用户
            client_id = self.room_handler.add_room(room, nick)
            # 给浏览器设置cookie,指定client_id
            self.set_cookie("client_id", client_id)
            self.render("mian.html", room_name=room)
        except tornado.web.MissingArgumentError:
            self.render("index.html")
        except RuntimeError as e:
            self.render("error.html", msg=str(e))
