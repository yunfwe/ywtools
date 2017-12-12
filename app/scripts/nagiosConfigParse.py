#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-12-12

def load(filename):
    f = open(filename,'rb')
    data = {}
    _tmp = {}
    start = False
    key = ''
    for i in f:
        i = i.decode('utf-8')
        i = i.strip()
        if ';' in i:
            i = i.split(';')[0].strip()
        if len(i) == 0:continue
        if i[0] == '#':continue
        if i[0] == '}':
            if not start: raise KeyError('}}}}}}}}')
        if i[:6] == 'define':
            if i[-1] != '{':raise KeyError('{{{{{{{{')
            start = True
            key = i.split()[-1][:-1]
            if data.get(key) is None:
                data[key] = []
            continue
        if i[0] == '}':
            if start:
                data[key].append(_tmp)
                _tmp = {}
            continue
        _d = i.split(None,1)
        _tmp[_d[0]] = _d[1]
    return data
