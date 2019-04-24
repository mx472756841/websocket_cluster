#!/usr/bin/python3
# -*- coding: utf-8
"""
@author: mx472756841@gmail.com
@file: urls.py
@time: 2019/1/26 17:08
"""
from tornado.web import url

from common.room_handler import room_handler
from handlers.ws.views import ChatHandler, MainHandler

urls = [
    url(r"/wss/chat", ChatHandler, {"room_handler": room_handler}),
    url(r"/", MainHandler, {"room_handler": room_handler}),
]
