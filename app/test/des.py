#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-11-07


class test(object):
    d = {}
    def __init__(self,msg=None):
        if msg is None: msg = '哈哈'
        self.msg = msg

    def __call__(self, func):
        def wrap(path=None):
            func(path)
            test.d[func.__name__] = path
        return wrap


@test('hehe')
def a(path):
    print(path)

@test('hehe')
def b(path):
    print(path)


if __name__ == '__main__':
    a()
    b(1)
    print(test.d)