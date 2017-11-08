#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-11-08

import ntplib

ntp = ntplib.NTPClient()
resp = ntp.request('cn.ntp.org.cn')
print(resp.tx_time)