#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-07

import socket
import traceback

addr,port = '0.0.0.0',1999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind((addr,port))
s.listen(10)
print('Server listen on %s:%s' % (addr,port))
try:
    c,a = s.accept()
    c.send(b'OK\r\n')
    c.close()
except KeyboardInterrupt as e:
    print('服务已关闭')


'''
import socket
addr,port = '192.168.8.253',999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((addr,port))
'''