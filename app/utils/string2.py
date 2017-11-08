#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-11-07

# 按照给定的字节分割字符串
class str2(str):
    def __init__(self, s):
        str.__init__(s)
    def lsplit2(self,n=1):
        s = self.__str__()
        return [s[i:i+n] for i in range(0, s.__len__(), n)]
    def rsplit2(self,n=1):
        s = self.__str__()
        return [s[i-n:i] for i in range(s.__len__(), -1,  -n)]


# IP地址转二进制数字
import binascii,socket
bin(int(binascii.hexlify(socket.inet_aton('127.0.0.1')).decode(),16))
socket.inet_ntoa(binascii.unhexlify(hex(int('0b1111111 00000000 00000000 00000001',2))[2:].encode()))