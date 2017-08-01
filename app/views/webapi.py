#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-01

import gevent.monkey;gevent.monkey.patch_all()

import os,subprocess
from app.core.memory import Memory
from bottle import response, Bottle
from app.utils.cache import wrapcache

app = Bottle()

@app.route('/meminfo')
@wrapcache(timeout=5)
def v_meminfo():
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
    return Memory.memBaseInfo()

@app.route('/pxestatus')
def v_pxestatus():
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
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
def v_pxestop(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
    rst = subprocess.Popen(['/usr/bin/killall', serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rst.wait()
    if rst.returncode == 0:
        return {'result':True}
    else:
        return {'result':False}

@app.route('/pxe/start/:serve')
def v_pxestart(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
    rst = subprocess.Popen([serve],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    rst.wait()
    if rst.returncode == 0:
        return {'result':True}
    else:
        return {'result':False}

@app.route('/pxe/restart/:serve')
def v_pxerestart(serve):
    if serve not in ['nginx','dnsmasq']:return ''
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
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
    app.run(server='gevent', host='0.0.0.0', port=8080)
