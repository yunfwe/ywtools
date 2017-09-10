#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import socket,sys

s = socket.fromfd(sys.stdin.fileno(),socket.AF_INET, socket.SOCK_STREAM)
s.sendall('Hello python!!!\r\n')
s.close()