#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-04-16

import sys
import socket
import binascii

s = socket.socket(2,1)
# s.connect(('16.190.200.208',21003))

content = sys.argv[2].replace('\\n','\n').decode('utf-8')
content = sys.argv[1]+';'+''.join(map(binascii.hexlify, content.encode('gbk')))+'\r\n'

open('/tmp/sms.log','a').write(content)