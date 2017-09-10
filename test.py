#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

import time
from sys import argv,stdout

def io(pid):
    with open('/proc/'+str(pid)+'/io') as f:
        raw = f.readlines()
        return dict(map(lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip()),raw))

def cov(num):
    num = int(num)
    if num > 1048576:
        return '%.3f MB' % (num/1048576.0)
    if num > 1024:
        return '%.3f KB' % (num/1024.0)
    else:
        return '%.3f B' % num

w_old_rst = None
r_old_rst = None
while True:
    rst = io(argv[1])
    w = int(rst['write_bytes'])
    r = int(rst['read_bytes'])
    if w_old_rst == r_old_rst is None:
        w_old_rst = w
        r_old_rst = r
    else:
        stdout.write('写入速度: %s/s\t读取速度: %s/s\r' % (cov(w-w_old_rst),cov(r-r_old_rst)))
        stdout.flush()
        w_old_rst = w
        r_old_rst = r
    time.sleep(1)

