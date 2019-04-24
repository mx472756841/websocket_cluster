#!/usr/bin/python3
# -*- coding: utf-8
""" 
@author: mx472756841@gmail.com
@file: room_handler.py
@time: 2019/1/26 15:15
长连接相关处理
"""
import datetime
import hashlib
import json
import logging
import re
import threading
import time
import uuid

from tornado.escape import json_encode, recursive_unicode

import settings
from common.db.redis import RedisClient

logger = logging.getLogger(__name__)


class RoomHandler(object):
    def __init__(self):
        # 房间信息 { room: [{'client_id':client_id, 'nick':'nick'}, {'client_id':client_id, 'nick':'nick'},], room1:[conn2, conn3]...}
        self.rooms_info = dict()
        # 临时连接信息 {client_id:{nick:'11', room:'222'}}
        self.temp_conns = dict()
        # 客户端信息 {client_id:{'conn':wsconn, 'nick':'11', 'room':'222'}}
        self.clients_info = dict()
        self.redis = RedisClient.get_client()

    def add_room(self, room, nick):
        """
        添加Room:
        1. 校验room相关信息
        2. 初始化room队列，并在pending中增加room信息，待到实际连接时再添加到room中
        3. 返回client_id，用于前台使用
        :param room: 房间名字
        :param nick: 用户名字
        :return: client_id
        """
        #: 校验房间和用户昵称的规则
        roomvalid = re.match(r'[\w-]+$', room)
        nickvalid = re.match(r'[\w-]+$', nick)
        if roomvalid == None:
            raise RuntimeError(
                "The room name provided was invalid. It can only contain letters, numbers, - and _.\nPlease try again.")
        if nickvalid == None:
            raise RuntimeError(
                "The nickname provided was invalid. It can only contain letters, numbers, - and _.\nPlease try again.")

        # 校验是否满足需求（数量限制，名字限制）
        with rlock:
            #: 校验是否单台服务器已经超限
            if len(self.rooms_info) > settings.MAX_ROOMS:
                raise RuntimeError(
                    "The maximum number of rooms (%d) has been reached.\n\nPlease try again later." % settings.MAX_ROOMS)
            #: 校验是否但房间已经超限
            if room in self.rooms_info and len(
                    self.rooms_info[room]) >= settings.MAX_USERS_PER_ROOM:
                raise RuntimeError(
                    "The maximum number of users in this room (%d) has been reached.\n\nPlease try again later." % settings.MAX_USERS_PER_ROOM)
            # 添加到房间中
            client_id = str(uuid.uuid4().int)
            if not self.rooms_info.get(room):
                self.rooms_info[room] = []

            # 验证nick是否已经重复, 应该从redis中获取用户昵称来验证
            # nicks = list(map(lambda x: x['nick'], self.rooms_info[room]))
            room_md5 = hashlib.md5(room.encode('utf-8')).hexdigest()
            nicks = recursive_unicode(self.redis.lrange(room_md5, 0, self.redis.llen(room_md5)))

            suffix = 1
            while True:
                if nick in nicks:
                    nick += str(1)
                else:
                    break
                suffix += 1

            # 将客户端的信息保存至temp_conns中
            self.temp_conns[client_id] = dict(room=room, nick=nick)
            return client_id

    def add_client(self, client_id, wsconn):
        """
        添加client_ws_conn
        1. 删除pending中的client
        2. 在room中实际添加连接
        3. 在client中实际添加信息
        4. 向房间所有人广播信息，同时更新房间人数列表
        :param client_id:
        :param wsconn:
        :return:
        """
        with rlock:
            # 在临时中取出client信息，并添加到clients_info中
            client_info = self.temp_conns.pop(client_id)
            client_info['conn'] = wsconn
            self.clients_info[client_id] = client_info

            # 在room中添加上连接信息
            self.rooms_info[client_info['room']].append(dict(
                nick=client_info['nick'],
                conn=wsconn,
                client_id=client_id
            ))

            # 用户列表放入redis缓存中
            room_md5 = hashlib.md5(client_info['room'].encode('utf-8')).hexdigest()
            self.redis.rpush(room_md5, client_info['nick'])
            nicks = recursive_unicode(self.redis.lrange(room_md5, 0, self.redis.llen(room_md5)))

        return {"room": client_info['room'], "nick": client_info['nick'], "nicks": nicks}

    def remove_client(self, client_id):
        """
        1. 在clients_info中移除client_id
        2. 在rooms_info中移除client，若是房间里没有人了，房间一并删除
        3. 通知房间内所有人。**离开房间
        4. 刷新房间在线人数列表
        :param client_id: 根据client_id通知信息
        :return:
        """
        # 在clients_info中移除client_id
        if client_id not in self.clients_info:
            return

        with rlock:
            client_info = self.clients_info.get(client_id)
            room = client_info['room']
            nick = client_info['nick']

            # 在rooms_info中移除room中的client
            room_client = list(filter(lambda x: x['client_id'] == client_id,
                                      self.rooms_info[room]))

            # 在redis中，将对应的用户移除
            room_md5 = hashlib.md5(room.encode('utf-8')).hexdigest()
            self.redis.lrem(room_md5, 0, nick)
            nicks = recursive_unicode(self.redis.lrange(room_md5, 0, self.redis.llen(room_md5)))
            # 将当前client在rooms中移除
            self.rooms_info[room].remove(room_client[0])

            # 将client在clients中移除
            del self.clients_info[client_id]

            # 移除room
            if len(self.rooms_info[room]) == 0:
                del self.rooms_info[room]

        return {"room": room, "nick": nick, "nicks": nicks}

    def send_msg(self, client_id, msg_type="join", message=None):
        """
        :param client_id: 客户端ID
        :param msg_type: 发送消息类型  join, leave, nicks
        :return:
        """
        client_info = self.clients_info.get(client_id)
        if client_info:
            room = client_info['room']
            nick = client_info['nick']
            conns = list(map(lambda x: x['conn'], self.rooms_info[room]))
            msg = dict(time='%10.6f' % time.time(),
                       msg_type=msg_type)
            if msg_type.lower() == 'join':
                msg['nick'] = nick
                msg['msg'] = 'joined the chat room.'
            elif msg_type.lower() == 'leave':
                msg['nick'] = nick
                msg['msg'] = 'left the chat room.'
            elif msg_type.lower() == 'nicks':
                msg['nick'] = nick
                msg['nicks'] = list(
                    map(lambda x: x['nick'], self.rooms_info[room]))
            elif msg_type.lower() == 'msg':
                msg['nick'] = nick
                msg['msg'] = message
            msg = json.dumps(msg)
            for conn in conns:
                conn.write_message(msg)


class EventHandler(object):
    """
        事件处理
    """

    def __init__(self, room):
        self.room = room

    def join(self, data):
        """
        加入房间，消息推送
        :param data:
        :return:
        """
        room_name = data['room']
        nickname = data['nick']
        event_data = {
            "msg_type": "join",
            "nick": nickname,
            "msg": "加入了房间。",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with rlock:
            rooms_info = self.room.rooms_info.get(room_name)
            if not rooms_info:
                logger.warning("无法获取到room信息[%s]" % rooms_info)
                return

            for client_info in rooms_info:
                ws_conn = self.room.clients_info.get(client_info['client_id'], None)
                if not ws_conn:
                    logger.warning("无法获取到用户信息[%s]" % client_info['client_id'])
                else:
                    ws_conn['conn'].write_message(json_encode(event_data))

    def send_message(self, data):
        """
        :param data:
        :return:
        """
        room_name = data['room']
        nickname = data['nick']
        msg = data['msg']
        event_data = {
            "msg_type": "send_message",
            "nick": nickname,
            "msg": msg,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with rlock:
            rooms_info = self.room.rooms_info.get(room_name)
            if not rooms_info:
                logger.warning("无法获取到room信息[%s]" % rooms_info)
                return

            for client_info in rooms_info:
                ws_conn = self.room.clients_info.get(client_info['client_id'], None)
                if not ws_conn:
                    logger.warning("无法获取到用户信息[%s]" % client_info['client_id'])
                else:
                    ws_conn['conn'].write_message(json_encode(event_data))

    def leave(self, data):
        """
        :param data:
        :return:
        """
        room_name = data['room']
        nickname = data['nick']
        event_data = {
            "msg_type": "leave",
            "nick": nickname,
            "msg": "离开了房间。",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with rlock:
            rooms_info = self.room.rooms_info.get(room_name)
            if not rooms_info:
                logger.warning("无法获取到room信息[%s]" % rooms_info)
                return

            for client_info in rooms_info:
                ws_conn = self.room.clients_info.get(client_info['client_id'], None)
                if not ws_conn:
                    logger.warning("无法获取到用户信息[%s]" % client_info['client_id'])
                else:
                    ws_conn['conn'].write_message(json_encode(event_data))

    def nicks(self, data):
        """
        :param data:
        :return:
        """
        nicks = data['nicks']
        room_name = data['room']
        event_data = {
            "msg_type": "nicks",
            "nicks": nicks,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with rlock:
            rooms_info = self.room.rooms_info.get(room_name)
            if not rooms_info:
                logger.warning("无法获取到room信息[%s]" % rooms_info)
                return

            for client_info in rooms_info:
                ws_conn = self.room.clients_info.get(client_info['client_id'], None)
                if not ws_conn:
                    logger.warning("无法获取到用户信息[%s]" % client_info['client_id'])
                else:
                    ws_conn['conn'].write_message(json_encode(event_data))


room_handler = RoomHandler()
event_handler = EventHandler(room_handler)
rlock = threading.RLock()
