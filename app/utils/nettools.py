#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-09

from __future__ import absolute_import
from __future__ import print_function

import os
import socket
import fcntl
import struct


# 获取主机网卡接口名称
def getInterface():
    # with open('/proc/net/dev') as f:
    #     raw = f.readlines()
    #     return tuple(map(lambda x:x.split(':')[0].strip(),raw[2:]))
    return tuple(os.listdir('/sys/class/net/'))

# 获取网卡的mac地址
def getMacByInterface(interface):
    try:
        return open('/sys/class/net/{inface}/address'
                    .format(inface=interface)).read().strip()
    except:
        return False

# 获取网卡绑定的IP地址
def getAddrByInterface(interface):
    interface = interface.encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])
    except:
        return False

# 通过DNS查询主机的IP地址
def getAddrInfo(host):
    try:
        return tuple(set(map(lambda x:x[4][0], socket.getaddrinfo(host,None))))
    except:
        return False

# DNS反向查询IP
def getHostByAddr(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return False

# 向目标主机发送ICMP包
def sendIcmpPackage(ip):
    pass

if __name__ == '__main__':
    for i in getInterface():
        print(i.ljust(15)+'\t'+getMacByInterface(i)+' '*10+str(getAddrByInterface(i)))