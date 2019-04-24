# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import

import logging.config
import os

# 当前目录所在路径

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
# 日志所在目录
LOG_PATH = os.path.join(BASE_PATH, 'logs')
# 临时存储目录
TEMP_PATH = os.path.join(BASE_PATH, 'temp')

# 是否调试模式
DEBUG = False

# 密码加密是的SECRET
SECRET_KEY = "Vda04BCdKJtGT2BATdLAmN9rPivqjnoLLC9k66H4IyRDInxKZqwtaZ4sLy5Z0C2f"

# 数据库配置(可通过自定义cfg.py修改)
MYSQL_DB_HOST = "127.0.0.1"
MYSQL_DB_PORT = 3306
MYSQL_DB_DBNAME = "root"
MYSQL_DB_USER = "root"
MYSQL_DB_PASSWORD = "123456"
MYSQL_IDLE_CONNECTIONS = 2000
MYSQL_MAX_RECYCLE_SEC = 600  # tornado_pymysql 连接池连接回收时间 单位:秒
MYSQL_CHARSET = "utf8mb4"
MYSQL_MAX_RECYCLE_TIMES = 50  # DButils 连接池,连接池连接回首次数
# mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
MYSQL_MIN_CACHED = 10
# maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
MYSQL_MAX_CACHED = 50

# 缓存Redis配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASS = ""
REDIS_DB = 0
REDIS_MAX_CONNECTIONS = 1000

# RabbitMQ相关配置
RABBIT_MQ_HOST = "127.0.0.1"
RABBIT_MQ_PORT = 5656
RABBIT_MQ_USER = "rabbitmq"
RABBIT_MQ_PASSWORD = "xz33xRaB0ywkpz41ygYU8"

# RabbitMQ相关队列配置
#: 业务订阅key使用      【前台收到请求，发送给后台，后台业务处理】
WEBSOCKET_SEND_EXCHANGE = "websocket_send_exchange"
#: websocket服务订阅key【后台通知给其他用户】
WEBSOCKET_LISTEN_EXCHANGE = "websocket_listen_exchange"

#: 长连接配置要求
MAX_ROOMS = 100
MAX_USERS_PER_ROOM = 10000

# *********************** tornado 配置 **********************
HOST = '127.0.0.1'
PORT = 9100
# *********************** tornado 配置 **********************

# 代码修改时, 是否自动重启
AUTO_RELOAD = True if DEBUG else False
# 可以给日志对象设置日志级别，低于该级别的日志消息将会被忽略
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING_HANDLERS = ['console'] if DEBUG else ['file']

# 日志模块配置
if not os.path.exists(LOG_PATH):
    # 创建日志文件夹
    os.makedirs(LOG_PATH)

if not os.path.exists(TEMP_PATH):
    # 创建日志文件夹
    os.makedirs(TEMP_PATH)


file_log_handler = {
    'level': 'DEBUG',
    # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
    'filename': os.path.join(LOG_PATH, 'server.log'),
    'formatter': 'verbose'
}
try:
    import cloghandler

    log_handler = {
        'class': 'cloghandler.ConcurrentRotatingFileHandler',
        # 当达到10MB时分割日志
        'maxBytes': 1024 * 1024 * 10,
        'backupCount': 10,
        # If delay is true,
        # then file opening is deferred until the first call to emit().
        'delay': True,
    }
except:
    log_handler = {
        'class': 'logging.handlers.TimedRotatingFileHandler'
    }

file_log_handler.update(log_handler)

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
        'file': file_log_handler
    },
    'loggers': {
        'tornado.curl_httpclient': {
            'handlers': LOGGING_HANDLERS,
            'level': 'INFO',
        },
        '': {
            'handlers': LOGGING_HANDLERS,
            'level': LOGGING_LEVEL,
        },
    }
})
# 执行自定义配置 如数据库等相关配置, 放在日志配置之前的原因,是日志会根据DEBUG变化而变化
etc_path = os.path.join(BASE_PATH, "etc", 'cfg.py')
if os.path.exists(etc_path):
    file = open(etc_path, 'r')
    text = file.read()
    file.close()
    try:
        exec(text)
    except Exception as e:
        print(e)
