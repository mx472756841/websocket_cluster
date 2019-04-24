#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: config.py
@time: 2019/4/24 15:21
"""
import logging.config
import os

# RABBITMQ相关配置
RABBIT_MQ_HOST = "127.0.0.1"
RABBIT_MQ_PORT = 5656
RABBIT_MQ_USER = "rabbitmq"
RABBIT_MQ_PASSWORD = "xz33xRaB0ywkpz41ygYU8"
# RabbitMQ相关队列配置
#: 业务订阅key使用      【前台收到请求，发送给后台，后台业务处理】
WEBSOCKET_SEND_EXCHANGE = "websocket_send_exchange"
#: websocket服务订阅key【后台通知给其他用户】
WEBSOCKET_LISTEN_EXCHANGE = "websocket_listen_exchange"

# 日志定义
LOGGING_LEVEL = 'DEBUG'
LOGGING_HANDLERS = ['file']
# 日志所在目录
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
LOG_PATH = os.path.join(BASE_PATH, 'logs')
# 日志模块配置
if not os.path.exists(LOG_PATH):
    # 创建日志文件夹
    os.makedirs(LOG_PATH)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(process)d] [%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
            'filename': os.path.join(LOG_PATH, 'server.log'),
            'formatter': 'verbose',
            'class': 'logging.handlers.TimedRotatingFileHandler'
        }
    }
})
