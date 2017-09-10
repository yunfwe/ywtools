#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-08

import sys,time
print("\033[31mWelcome.\033[0m")
print("Please enter a string:")
sys.stdout.flush()
line = sys.stdin.readline().strip()
print("You entered %s..." % line)
for i in range(100):
    sys.stdout.write('%s\r' % i)
    sys.stdout.flush()
    time.sleep(0.1)