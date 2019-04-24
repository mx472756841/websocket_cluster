#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: room_handler.py
@time: 2019/1/26 15:15

"""
import logging
import config
from rabbitmq import RabbitMQClient

logger = logging.getLogger(__name__)


class EventHandler(object):
    """
    事件处理
    """

    def join(self, data):
        """
        加入房间
        :param data:
        :return:
        """
        send_data = {
            "type": "join",
            "data": data
        }
        rabbitmq_client = RabbitMQClient()
        rabbitmq_client.publish_message(send_data, config.WEBSOCKET_LISTEN_EXCHANGE,
                                        config.WEBSOCKET_LISTEN_EXCHANGE, exchange_type='fanout')

    def leave(self, data):
        """
        离开房间
        :param data:
        :return:
        """
        send_data = {
            "type": "leave",
            "data": data
        }
        rabbitmq_client = RabbitMQClient()
        rabbitmq_client.publish_message(send_data, config.WEBSOCKET_LISTEN_EXCHANGE,
                                        config.WEBSOCKET_LISTEN_EXCHANGE, exchange_type='fanout')

    def nicks(self, data):
        """
        人数变化
        :param data:
        :return:
        """
        send_data = {
            "type": "nicks",
            "data": data
        }
        rabbitmq_client = RabbitMQClient()
        rabbitmq_client.publish_message(send_data, config.WEBSOCKET_LISTEN_EXCHANGE,
                                        config.WEBSOCKET_LISTEN_EXCHANGE, exchange_type='fanout')

    def send_message(self, data):
        """
        发送消息
        :param data:
        :return:
        """
        send_data = {
            "type": "send_message",
            "data": data
        }
        rabbitmq_client = RabbitMQClient()
        rabbitmq_client.publish_message(send_data, config.WEBSOCKET_LISTEN_EXCHANGE,
                                        config.WEBSOCKET_LISTEN_EXCHANGE, exchange_type='fanout')


def recursive_unicode(obj):
    """Walks a simple data structure, converting byte strings to unicode.

    Supports lists, tuples, and dictionaries.
    """
    if isinstance(obj, dict):
        return dict((recursive_unicode(k), recursive_unicode(v)) for (k, v) in obj.items())
    elif isinstance(obj, list):
        return list(recursive_unicode(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_unicode(i) for i in obj)
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    else:
        return obj
