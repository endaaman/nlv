# nico.py
#
# Copyright (c) 2017 endaaman
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.

import re
import socket
import select
from xml.etree import ElementTree
import requests
from pyquery import PyQuery as pq
from config import Config


class LiveInfo:
    def __init__(self, nico, id, title=None, load_status=False):
        self.nico = nico
        self.id = id
        self.title = title

        self.is_status_loaded = False
        self.ms_addr = None
        self.ms_port = None
        self.ms_thread = None
        if load_status:
            self.loadStatus()

    def loadStatus(self):
        if self.is_status_loaded:
            return
        r = requests.get('http://live.nicovideo.jp/api/getplayerstatus?v=lv%s' % self.id, cookies={
            'user_session': self.nico.config.getSession()
        })
        elem = ElementTree.fromstring(r.content)
        self.is_status_loaded = True
        self.title = elem.find('.//title').text
        ms = elem.find('.//ms')
        self.ms_addr = ms.find('.//addr').text
        self.ms_port = ms.find('.//port').text
        self.ms_thread = ms.find('.//thread').text

    def get_sock(self):
        self.loadStatus()
        sock = LiveSocket(self.ms_addr, self.ms_port, self.ms_thread)
        return sock

class LiveSocket:
    def __init__(self, addr, port, thread):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((addr, int(port)))
        msgthread = str(thread)
        resfrom = '20'
        initsend = '<thread thread="%s" version="20061206" res_from="-%s"/>' % (msgthread, resfrom)
        self.sock.send(initsend.encode("utf-8"))
        self.sock.send(b"\x00")

    def recieve(self, recv_buffer=4096, delim='\n'):
        buffer = ''
        data = True
        while data:
            data = self.sock.recv(recv_buffer)
            buffer += data.decode('utf-8')
            while buffer.find(delim) != -1:
                line, buffer = buffer.split('\n', 1)
                yield line

    def close(self):
        self.sock.close()


class Nico:
    def __init__(self):
        self.config = Config()
        self.lives = {}

    def load_lives(self):
        self.lives = {}
        r = requests.get('http://www.nicovideo.jp/my/live', cookies={
            'user_session': self.config.getSession()
        })
        d = pq(r.content)
        for h5 in d('h5'):
            el = d(h5)
            title = el.text()
            href = el('a').attr['href']
            id = re.findall(r'live.nicovideo.jp/watch\/lv(.+?)\?ref=', href)[0]
            self.lives[id] = LiveInfo(self, id, title)

    def load_live(self, id):
        live = self.lives.get(id)
        if not live:
            self.lives[id] = LiveInfo(self, id, load_status=True)

    def connect(self, id):
        self.load_live(id)
        live = self.lives.get(id)
        return live.get_sock()

