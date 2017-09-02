#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-31

import os
import time
import sys,pwd

child_process = []

print('before fork')
for i in range(10):
    pid = os.fork()
    print('after fork')
    ppid = os.getppid()

    if pid == 0:
        os.setuid(1000)
        os.setsid()
        print('This is child process pid:%s,ppid:%s' % (os.getpid(),ppid))
        time.sleep(100)
    else:
        print('This is parent process pid:%s' % pid)
os.wait()

