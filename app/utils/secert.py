#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-01-16

# unix系统用户加密
import crypt
crypt.crypt('password',salt=crypt.mksalt())
# salt参数为None的话 默认就会调用crypt.mksalt()