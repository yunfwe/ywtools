#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-06

from __future__ import absolute_import
from __future__ import print_function

class Memory(object):
    f_meminfo = '/proc/meminfo'
    # f_meminfo = 'proc/meminfo'

    @staticmethod
    def memInfo():
        with open(Memory.f_meminfo) as f:
            raw = [x for x in f.read().split('\n') if x]
            data = map(lambda x:(x.split(':')[0],x.split(':')[1].strip()), raw)
            return dict(map(lambda x:(x[0],int(x[1].split()[0])*1024), data))

    @staticmethod
    def memBaseInfo():
        _info = Memory.memInfo()
        _mem = {'MemTotal': _info['MemTotal'], 'MemFree': _info['MemFree'], 'Buffers': _info['Buffers'],
                'Cached': _info['Cached'], 'SwapTotal': _info['SwapTotal'], 'SwapCached': _info['SwapCached'],
                'SwapFree': _info['SwapFree']}
        return _mem

    @staticmethod
    def getMemUsedFromPid():
        pass

if __name__ == '__main__':
    print(Memory.memInfo())
