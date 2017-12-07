#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-05

from __future__ import print_function

from app.test.netscan import netscan

iprange = []
for i in range(1,255):
    iprange.append('192.168.88.'+str(i))

result = netscan(iprange, threads=255)
for i in result:
    print('ip: %s is %s' % i)

alive = filter(lambda x:x[1] is True, result)
print(len(alive))


# 一行代码的随机数
import random
rdm = lambda x:''.join(map(chr,[random.choice(range(97,123)) for _ in range(x)]))