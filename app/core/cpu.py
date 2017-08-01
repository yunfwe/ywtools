#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-06

class Cpu(object):
    # f_cpuinfo = '/proc/cpuinfo'
    f_cpuinfo = '/proc/cpuinfo'

    @staticmethod
    def cpuInfo():
        with open(Cpu.f_cpuinfo) as f:
            raw = [x for x in f.read().split('\n\n') if x]
            handler = lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip())
            return map(lambda x:dict(map(handler, x.split('\n'))),raw)


if __name__ == '__main__':
    # print(Cpu.cpuInfo())
    pass