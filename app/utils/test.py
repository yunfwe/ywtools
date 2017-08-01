#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-05

from __future__ import  print_function

from app.tools.netscan import netscan


iprange = []
for i in range(1,255):
    iprange.append('192.168.88.'+str(i))

result = netscan(iprange, threads=255)
for i in result:
    print('ip: %s is %s' % i)

alive = filter(lambda x:x[1] is True, result)
print(len(alive))

