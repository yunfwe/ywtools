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

def dump(data):
    cfg = ''
    klen = 10
    for k in data.keys():
        for i in data[k]:
            for b in i.items():
                if len(b[0]) > klen:klen = len(b[0])+4
    print(klen)
    for k in data.keys():
        for i in data[k]:
            head = 'define %s{\n' % k
            body = ''
            for b in i.items():
                body += '       '+b[0].ljust(klen)+b[1]+'\n'
            foot = '}\n\n'
            cfg += head+body+foot
    return cfg

