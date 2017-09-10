#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import socket

addr,port = '0.0.0.0',19999

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((addr,port))
print("Server listen on %s:%s" % (addr,port))

while True:
    try:
        msg, addr = s.recvfrom(8192)
        print("Got data from %s, data: %s" % (addr, msg))
        s.sendto(b"I am here", addr)
    except (KeyboardInterrupt, SystemExit):
        print("程序退出")
        exit(0)