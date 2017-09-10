#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import socket
dest = ('<broadcast>', 19999)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto(b'Hello', dest)
print("Received from %s: %s" % s.recvfrom(2048))