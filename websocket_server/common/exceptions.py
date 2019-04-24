#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: exceptions.py
@time: 2018/11/22 15:40
"""


class NormalException(BaseException):

    def __init__(self, *args, **kwargs):
        self.msg = kwargs.get('msg', '未知错误')
