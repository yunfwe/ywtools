#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-09

import socket

def getaddrinfo(host):
    return tuple(set(map(lambda x:x[4][0],socket.getaddrinfo(host,None))))