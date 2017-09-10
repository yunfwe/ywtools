#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-10

import os

# def getLibPath(lib):
#     with open('/etc/ld.so.cache','rb') as f:
#         libs = []
#         data = {}
#         for i in f.read().split(b'\x00'):
#             try:
#                 _tmp = i.decode()
#                 if _tmp.startswith('/'):
#                     libs.append(_tmp)
#             except:
#                 pass
#         for i in libs:
#             data[i.split('/')[-1]] = i
#         return data.get(lib,False)

# 根据库文件名找到绝对路径
def getLibPath(ld):
    with open('/etc/ld.so.cache', 'rb') as f:
        data = f.read().split(b'\x00')
        try:
            ldpath = data[data.index(ld.encode()) + 1]
            return ldpath.decode()
        except:
            return False


# 列出ELF可执行程序依赖库
def ldd(fn, need=False):
    needs = [
        'libresolv.so.2',
        'libnss_dns.so.2',
        'libnss_files.so.2',
        'libgcc_s.so.1',
    ]
    deplibs = []
    _tmp = os.popen('ldd ' + fn).readlines()
    _tmp = [x.split('=>')[0].strip() for x in _tmp]
    for i in _tmp:
        if 'linux-vdso.so.1' in i or 'ld-linux-x86-64.so.2' in i: continue
        deplibs.append(i)
    if need: deplibs += needs
    deplibs.append('ld-linux-x86-64.so.2')
    return deplibs


if __name__ == '__main__':
    # print(getLibPath('libSegFault.sos'))
    for i in ldd('/bin/bash',True):
        print('%s  =>  %s' % (i.ljust(20),getLibPath(i)))
