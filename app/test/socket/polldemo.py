#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import socket,time,select

host, port = '', 1999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
s.listen(5)
print("Server listen on %s:%s" % (host, port))

p = select.poll()
p.register(s.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP)

while True:
    rst = p.poll(50)
    c, a = s.accept()
    c.send(time.asctime().encode()+b'\n')
    time.sleep(5)
    c.close()