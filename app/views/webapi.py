#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-01

import gevent.monkey;gevent.monkey.patch_all()

import os,subprocess
from app.core.memory import Memory
from bottle import  Bottle, run
from app.utils.cache import wrapcache
from app.utils.bottle_ext import allowOrigin

app = Bottle()

@app.route('/meminfo')
@allowOrigin
@wrapcache(timeout=5)
def v_meminfo():
    return Memory.memBaseInfo()

@app.route('/pxe/status')
@allowOrigin
@wrapcache(timeout=0.5)
def v_pxestatus():
    nginxPid = os.popen('pgrep nginx').readlines()
    dnsmasqPid = os.popen('pgrep dnsmasq').readlines()
    if not nginxPid: nginxPid = None
    else: nginxPid = nginxPid[0].strip()
    if not dnsmasqPid: dnsmasqPid = None
    else: dnsmasqPid = dnsmasqPid[0].strip()
    def getPort(port):
        rst = os.popen(r'netstat -anptu |grep "\b:%s\b"' % port).read()
        if rst:return True
        return False
    return {
        'processes': [
            {'name': 'nginx','pid': nginxPid},
            {'name': 'dnsmasq', 'pid': dnsmasqPid}
        ],
        'ports': [
            {'port':80, 'type':'tcp', 'status': getPort(80)},
            {'port':67, 'type':'udp', 'status': getPort(67)},
            {'port':69, 'type':'udp', 'status': getPort(69)},
        ]
    }

@app.route('/pxe/stop/:serve')
@allowOrigin
def v_pxestop(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    rst = subprocess.Popen(['/usr/bin/killall', serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rst.wait()
    if rst.returncode == 0:
        return {'result':True}
    else:
        return {'result':False}

@app.route('/pxe/start/:serve')
@allowOrigin
def v_pxestart(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    rst = subprocess.Popen([serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rst.wait()
    if rst.returncode == 0:
        return {'result':True}
    else:
        return {'result':False}

@app.route('/pxe/restart/:serve')
@allowOrigin
def v_pxerestart(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    subprocess.Popen(['/usr/bin/killall', serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE).wait()
    rst = subprocess.Popen([serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rst.wait()
    if rst.returncode == 0:
        return {'result':True}
    else:
        return {'result':False}


if __name__ == '__main__':
    run(app=app, server='gevent', host='0.0.0.0', port=8080, reloader=True)
