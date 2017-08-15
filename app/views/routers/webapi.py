#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-01


import os,subprocess,json

from app.core.memory import Memory
from app.utils.cache import wrapcache
from app.utils.bottle_ext import allowOrigin
from app.tools.netscan import ping

from app.tools.IPy import IP
from bottle import  Bottle, run, request, abort

api = Bottle()

@api.route('/meminfo')
@allowOrigin
@wrapcache(timeout=5)
def v_meminfo():
    return Memory.memBaseInfo()

@api.route('/pxe/status')
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

@api.route('/pxe/stop/:serve')
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

@api.route('/pxe/start/:serve')
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

@api.route('/pxe/restart/:serve')
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

@api.route('/pyinfo')
def v_pyinfo():
    from app.tools.pyinfo import pyinfo
    return pyinfo()

@api.route('/ws/ping')
def ws_ping():
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    # while True:
    try:
        iprange = ws.receive()
        ips = []
        if ',' in iprange:
            ips = iprange.split(',')
        elif '-' in iprange:
            s,e = list(map(int,iprange.split('.')[-1].split('-')))
            for i in range(s,e+1):
                ips.append('.'.join(iprange.split('-')[0].split('.')[:3])+'.'+str(i))
        elif '/' in iprange:
            ips = list(map(lambda x:x.__str__(),IP(iprange)))[1:-1]
        else:
            ips.append(iprange)
        if not ips:ws.close();
        for ip in ips:
            ws.send(json.dumps(ping(ip)))
    except WebSocketError:
        # break
        pass
    finally:
        ws.close()


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(("0.0.0.0", 8080), api,
                        handler_class=WebSocketHandler)
    server.serve_forever()
    # run(app=app, server='gevent', host='0.0.0.0', port=8080, reloader=True)
