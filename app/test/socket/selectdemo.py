#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import socket,select

host, port = '', 1999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
s.listen(5)
print("Server listen on %s:%s" % (host, port))

inputs = [s]

while True:
    r,w,e = select.select(inputs,[],[],10)
    for i in r:
        if i is s:
            c,a = s.accept()
            inputs.append(c)
        else:
            data = i.recv(1024)
            if data:
                if data == b'exit\r\n':
                    i.close()
                    inputs.remove(i)
                    print("Remove %s" % str(a))
                    continue
                print("Got data: %s" % data.decode('utf-8',errors='ignore'))
                i.send(b'hehe\r\n')
            else:
                inputs.remove(i)
                print("Remove %s" % str(a))

