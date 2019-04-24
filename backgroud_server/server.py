#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: server.py
@time: 2019/4/24 15:17
"""
import json
import logging
import threading

import config
from event import EventHandler, recursive_unicode
from rabbitmq import RabbitMQClient

logger = logging.getLogger(__name__)


def rabbitmq_callback(ch, method, properties, body):
    """
        @ch: channel 通道，是由外部调用时上送
        out body
        读取队列内容做不同的操作
    """
    event_handler = EventHandler()
    d_item = json.loads((recursive_unicode(body)))
    try:
        h_type = d_item['type']
        h_data = d_item['data']
        if hasattr(event_handler, h_type):
            func = getattr(event_handler, h_type)
            try:
                # 使用多线程处理
                t = threading.Thread(target=func, args=(h_data,))
                t.start()
            except:
                logger.exception("处理失败 [{}]".format(d_item))
        else:
            logger.error("暂时不支持的操作类型[{}] 操作内容[{}]".format(h_type, h_data))
    except:
        logger.exception("解析内容失败：{}".format(d_item))


def run():
    conn = None
    try:
        client = RabbitMQClient()
        # get channel
        channel = client.get_channel(config.WEBSOCKET_SEND_EXCHANGE, exchange_type='direct')
        # 声明临时队列 , param exclusive 排他  durable 持久化
        queue_name = '{}_task_queue'.format(config.WEBSOCKET_SEND_EXCHANGE)
        channel.queue_declare(durable=True, queue='{}_task_queue'.format(config.WEBSOCKET_SEND_EXCHANGE))
        channel.queue_bind(exchange=config.WEBSOCKET_SEND_EXCHANGE,
                           queue=queue_name,
                           routing_key=config.WEBSOCKET_SEND_EXCHANGE)
        # 在队列中读取信息
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(rabbitmq_callback, queue=queue_name, no_ack=True)
        channel.start_consuming()
    except:
        logger.exception("处理失败")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    run()
