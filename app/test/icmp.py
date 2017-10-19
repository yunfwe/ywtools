#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import struct
def checksum(source_string):
    s = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        s = s + thisVal
        s = s & 0xffffffff
        count = count + 2
    if countTo<len(source_string):
        s = s + ord(source_string[len(source_string) - 1])
        s = s & 0xffffffff
    s = (s >> 16)  +  (s & 0xffff)
    s = s + (s >> 16)
    answer = ~s
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer
def ping(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
    packet = struct.pack(
            "!BBHHH", 8, 0, 0, 0, 0
    )
    chksum=checksum(packet)
    packet = struct.pack(
            "!BBHHH", 8, 0, chksum, 0, 0
    )
    s.sendto(packet, (ip, 1))
    print(s.recvfrom(100))
if __name__=='__main__':
    ping('192.168.41.56')