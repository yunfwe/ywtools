#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import time


# 计算函数运行耗时
def timeit(func):
    def _func(*args,**kwargs):
        now = time.time()
        rst = func(*args,**kwargs)
        return rst,time.time()-now
    return _func


def datetime():
    return time.strftime('%Y-%m-%d %H:%M:%S')