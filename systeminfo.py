#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei date: 2017-07-03

import os
from glob import glob

def cpuinfo():
    with open('/proc/cpuinfo') as f:
        raw = [x for x in f.read().split('\n\n') if x]
        handler = lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip())
        return map(lambda x:dict(map(handler, x.split('\n'))),raw)

def meminfo():
    with open('/proc/meminfo') as f:
        # 按行分割去掉空白字符串
        raw = [x for x in f.read().split('\n') if x]
        # 用':'分割后 转为元祖 最后转为字典
        return dict(map(lambda x:(x.split(':')[0],x.split(':')[1].strip()), raw))

# 网卡流量统计
def netinfo():
    with open('/proc/net/dev') as f:
        raw = f.readlines()
        keys = raw[1].replace('|',' ').split()
        inface = map(lambda x:x.replace(':',' ').split(),raw[2:])
        _netinfo = {}
        for x in inface:
            _i = dict(zip(keys[1:9],x[1:9]))
            _o = dict(zip(keys[9:],x[9:]))
            _netinfo[x[0]] = {'in':_i,'out':_o}
        return _netinfo

def processinfo():
    pids = glob('/proc/[1-9]*')
    processes = []
    for pid in pids:
        info = {}
        info['pid'] = os.path.basename(pid)
        info['exe'] = os.path.realpath(pid+'/exe') if os.path.exists(pid+'/exe') else ''
        info['cwd'] = os.path.realpath(pid+'/cwd') if os.path.exists(pid+'/cwd') else ''
        with open(pid+'/cmdline','r') as f:
            info['cmdline'] = f.read().replace('\x00',' ').strip()
        with open(pid+'/comm','r') as f:
            info['comm'] = f.read().strip()
        with open(pid+'/limits','r') as f:
            raw = f.readlines()
            keys = [x.strip() for x in raw[0].strip().split(' '*4) if x]
            info['limits'] = []
            for i in raw[1:]:
                values = [x.strip() for x in i.strip().split(' '*4) if x]
                info['limits'].append(dict(zip(keys,values)))
        with open(pid+'/status','r') as f:
            raw = f.readlines()
            info['status'] = dict(map(lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip()),raw))
        with open(pid+'/environ') as f:
            raw = [x for x in f.read().split('\x00') if x]
            # info['environ'] = dict(map(lambda x:(x.split('=',1)[0],x.split('=',1)[1]),raw))
            _tmp = []
            for i in raw:
                _d = i.split('=',1)
                if len(_d) == 2:
                    _tmp.append((_d[0],_d[1]))
                elif len(_d) == 1:
                    _tmp.append((_d[0],''))
            info['environ'] = dict(_tmp)
        info['fd'] = []
        for i in os.listdir(pid+'/fd'):
            info['fd'].append(os.path.realpath(pid+'/fd/'+i))

        with open(pid+'/io') as f:
            raw = f.readlines()
            info['io'] = dict(map(lambda x:(x.split(':')[0].strip(),x.split(':')[1].strip()),raw))
        yield info

# tcp/udp 统计

socket_state = {
    '01': 'TCP_ESTABLISHED',
    '02': 'TCP_SYN_SEND',
    '03': 'TCP_SYN_RECV',
    '04': 'TCP_FIN_WAIT1',
    '05': 'TCP_FIN_WAIT2',
    '06': 'TCP_TIME_WAIT',
    '07': 'TCP_CLOSE',
    '08': 'TCP_CLOSE_WAIT',
    '09': 'TCP_LAST_ACK',
    '0A': 'TCP_LISTEN',
    '0B': 'TCP_CLOSING'
}

def tcpstat():
    pass

def udpstat():
    pass

def diskinfo():
    pass