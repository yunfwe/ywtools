#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-06

from __future__ import absolute_import
from __future__ import print_function

import platform
import socket

from subprocess import Popen,PIPE
from multiprocessing.dummy import Pool as ThreadPool


def ping(ip):
    if platform.system() == 'Windows':
        process = Popen(['ping','-n','2','-w','1', ip], stdout=PIPE, stderr=PIPE)
    else:
        process = Popen(['ping','-i','0.2','-c','2','-W','1', ip], stdout=PIPE, stderr=PIPE)
    process.communicate()
    if process.returncode == 0:
        return ip, True
    else:
        return ip, False

def netscan(iprange,threads=10):
    pool = ThreadPool(threads)
    result = pool.map(ping, iprange)
    return result

def tcpPortScan(ip, ports=None):
    if ports is None:
        ports = []
    assert isinstance(ports,list), 'Port must to be list<int>'
    if not ports:
        ports = range(1,1025)
    result = []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((ip,int(p))) == 0:
            s.close()
            result.append((p, True))
        else:
            s.close()
            result.append((p, False))
    return result


def tcpPortLazyScan(ip, ports=None):
    if ports is None:
        ports = []
    assert isinstance(ports,list), 'Port must to be list<int>'
    if not ports:
        ports = range(1,1025)
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((ip,int(p))) == 0:
            s.close()
            yield p, True
        s.close()
        yield p, False

if __name__ == '__main__':
    pass