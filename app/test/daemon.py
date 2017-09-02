#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-31

import os,pwd
import time
from sys import argv

pid = os.fork()
if pid:exit()
subpid = os.getpid()
os.setuid(1000)
os.setsid()
open('/tmp/pid.log','a').write('[python]: subprocess run on '+str(subpid))
time.sleep(100000)