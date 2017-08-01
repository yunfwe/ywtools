#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function

import time
from sys import argv

def io(pid):
    with open('/proc/'+str(pid)+'/io') as f:
        raw = f.readlines()
        return dict(map(lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip()),raw))

w_old_rst = None
r_old_rst = None
while True:
    rst = io(argv[1])
    w = int(rst['write_bytes'])
    r = int(rst['read_bytes'])
    if w_old_rst == r_old_rst == None:
        w_old_rst = w
        r_old_rst = r
    else:
        print('Pid: %s\n写入速度: %s MB/s\n读取速度: %s MB/s' % (argv[1],(w-w_old_rst)/1024.0/1024.0,(r-r_old_rst)/1024.0/1024.0))
        w_old_rst = w
        r_old_rst = r
    time.sleep(1)

