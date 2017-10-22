#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-19

import time
from multiprocessing.dummy import Pool as ThreadPool

def myprint(msg):
    print("开始处理 %s" % msg)
    if msg == 4:
        raise Exception("异常")
    time.sleep(3)
    return "done %s" % msg

if __name__ == '__main__':
    print(__import__('os').getpid())
    pool = ThreadPool(4)
    rst = pool.map_async(func=myprint, iterable=range(10))
    print(rst.ready())
    print(rst.get())
    rst.successful()
    print(rst)