#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
统计最快速度和最慢速度
自定义测试时间
生成简易终端图表
完成上传和下载速率统计
"""


import time
import socket
import threading

s = socket.socket()
s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
s.bind(('0.0.0.0',11190))
s.listen(5)
c,addr = s.accept()

class sendPack(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.next = True
        self.count = 0
        self.packsize = 4096
        self.packdata = b'\x00'

    def run(self):
        while self.next:
            c.send(self.packsize*self.packdata)
            self.count += 1
        c.close()

sd = sendPack()
sd.start()
time.sleep(10)
print('上传速度： %.2f MB/s'% ((sd.count*sd.packsize)/10/1024.0/1024.0))
print('上传速率： %.2f Mbps'% ((sd.count*sd.packsize)*8/10/1024.0/1024.0))
sd.next = False