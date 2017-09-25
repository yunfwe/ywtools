#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-21

from __future__ import absolute_import,print_function

# from gevent import monkey;monkey.patch_all()

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import time
import queue
import threading

import bottle
import pymysql
import requests
import dracclient.client
import urllib3;urllib3.disable_warnings()


dbConfig = {
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "123456",
    "db": "test",
    "port": 3306,
    "charset": "utf8",
    "autocommit": True
}

class fieldMap(object):
    # 表名
    table       = 'mrtg.xxx'
    # 下面是字段映射
    id          = 'id'              # 主键
    hostip      = 'ip'              # 主机IP
    ipmiip      = 'ipmi'            # IPMI接口IP
    ipmiUser    = 'root'            # IDRAC登陆用户
    ipmiPass    = 'calvin'          # IDRAC登陆密码
    status      = 'status'          # 0-OFF  1-ON  2-REBOOT  3-NULL
    position    = 'position'        # 所在机房位置


class idrac(object):
    def __init__(self, ip, username, password):
        self.ip,self.username,self.password = ip,username,password
        self.client = dracclient.client.DRACClient(ip,username,password)

    def ping(self):
        # return True
        try:
            return {'200':True}.get(str(requests.get(
                'https://{ip}/login.html'.format(ip=self.ip),
                verify=False,timeout=5).status_code),False)
        except:
            return False

    def getPowerState(self):
        """
        :return: 'POWER_ON', 'POWER_OFF' or 'REBOOT'
        """
        # return 'POWER_ON'
        try: return self.client.get_power_state()
        except: return False

    # def setPowerState(self,state):
    #     """
    #     :param state: 'POWER_ON', 'POWER_OFF' or 'REBOOT'
    #     :return: True or False
    #     """
    #     if self.ping():
    #         try:
    #             if self.client.set_power_state(state) is None:return True
    #             else: return False
    #         except: return False
    #     else: return False
    def setPowerState(self,state):
        # return True
        """
        :param state: 'POWER_ON', 'POWER_OFF' or 'REBOOT'
        :return: True or False
        """
        try:
            if self.client.set_power_state(state) is None:return True
            else: return False
        except: return False

# {'id':{'ip':'127.0.0.1','username':'root','password':'calvin','hostip':'127.0.0.1'}}
hostinfo = {}
hostinfo = {'1':{'ip':'127.0.0.1','username':'root','password':'calvin','hostip':'127.0.0.1'}}

# [(id,operation)] (1,'ON')  ON OFF REBOOT
process = []
processLock = threading.Lock()

taskQueue = queue.Queue()
result = []
rstLock = threading.Lock()

threadnum = 10
threadPool = []
threadPoolLock = threading.Lock()


class HandlerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.status = 'start'
        self.setDaemon(True)
        self.setName('Handler Thread')
        with threadPoolLock: threadPool.append(self)

    def run(self):
        while True:
            # with taskLock: task = tasks.pop()
            # if not self.next:return
            self.status = 'pendding'
            task = taskQueue.get()
            if task == 'stopall':
                with threadPoolLock: threadPool.remove(self)
                if len(threadPool) > 0:taskQueue.put('stopall')
                print(self.getName()+' exit')
                return
            if task == 'stop':
                with threadPoolLock: threadPool.remove(self)
                print(self.getName()+' exit')
                return
            self.status = 'running'
            info = hostinfo.get(task[0])
            with processLock:process.append(task[0])
            self.setName('Handler Thread (%s)'%info['ip'])
            cli = idrac(info['ip'],info['username'],info['password'])
            time.sleep(10)
            ping = cli.ping()
            time.sleep(3)
            print(self.getName()+' run done')
            if not ping:
                with rstLock: result.append((task[0],'connect error'))
                with processLock:process.remove(task[0])
                continue
            curstate = cli.getPowerState()
            if not curstate:
                with rstLock: result.append((task[0],'cannot get status infomation'))
                with processLock:process.remove(task[0])
                continue
            if curstate == 'REBOOT':
                with rstLock: result.append((task[0],'power is reboot'))
                with processLock:process.remove(task[0])
                continue
            if task[1] == 'ON':
                if curstate == 'POWER_ON':
                    with rstLock: result.append((task[0],'power is on'))
                    with processLock:process.remove(task[0])
                    continue
                if curstate == 'POWER_OFF':
                    state = cli.setPowerState('POWER_ON')
                    if not state:
                        with rstLock: result.append((task[0],'boot failed'))
                        with processLock:process.remove(task[0])
                        continue
                    with rstLock: result.append((task[0],'boot successful'))
                    with processLock:process.remove(task[0])
                    continue
            elif task[1] == 'OFF':
                if curstate == 'POWER_OFF':
                    with rstLock: result.append((task[0],'power is off'))
                    with processLock:process.remove(task[0])
                    continue
                if curstate == 'POWER_ON':
                    state = cli.setPowerState('POWER_OFF')
                    if not state:
                        with rstLock: result.append((task[0],'shutdown failed'))
                        with processLock:process.remove(task[0])
                        continue
                    with rstLock: result.append((task[0],'shutdown successful'))
                    with processLock:process.remove(task[0])
                    continue
            elif task[1] == 'REBOOT':
                state = cli.setPowerState('REBOOT')
                if not state:
                    with rstLock: result.append((task[0],'reboot failed'))
                    with processLock:process.remove(task[0])
                    continue
                with rstLock: result.append((task[0],'reboot successful'))
                with processLock:process.remove(task[0])
                continue

class CheckThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.setName('Check Thread')
        self.status = 'running'
        with threadPoolLock: threadPool.append(self)
    def run(self):
        time.sleep(1000)

class LogThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.setName('Log Thread')
        self.status = 'running'
        with threadPoolLock: threadPool.append(self)
    def run(self):
        time.sleep(1000)

CheckThread().start()
LogThread().start()
for i in range(threadnum):
    HandlerThread().start()

app = bottle.Bottle()

@app.route('/idrac/status')
def idrac_status():
    pass

@app.route('/idrac/status/<ip>')
def idrac_status_ip(ip):
    pass

@app.route('/idrac/control', method=['POST'])
def idrac_control():
    """
    {
	    "id":[1,2,3,4],
	    "option":"ON"
    }
    :return: 
    """
    try:
        ids = bottle.request.json.get('id')
        option = bottle.request.json.get('option')
        if option not in ["ON","OFF","REBOOT"]:return {"msg":"error option"}
    except:
        return {"msg":"error"}


    print(bottle.request.json.get('id'))
    print(bottle.request.headers.get('Content-Type'))
    return {"msg":"ok"}

























@app.route('/start/<num>')
def start(num):
    for i in range(int(num)):
        HandlerThread().start()

@app.route('/stop/<num>')
def index(num):
    for i in range(int(num)):
        taskQueue.put('stop')
    return 'ok\n'

@app.route('/stopall')
def index():
    taskQueue.put('stopall')
    return 'ok\n'

@app.route('/result')
def v_status():
    return str(result)+'\n'

@app.route('/show')
def v_show():
    for i in threadPool:
        yield "%s\t\t%s\n"%(i.getName(),i.status)

@app.route('/process')
def v_show():
    for i in process:
        yield i+"\n"

@app.route('/ip')
def v_ip():
    for i in range(100):
        taskQueue.put(('1','REBOOT'))
    return 'add ok\n'

@app.route('/loop')
def v_loop():
    for i in range(100):
        time.sleep(1)
        yield str(i)+'\n'

@app.route('/echo')
def echo():
    ws = bottle.request.environ.get('wsgi.websocket')
    while True:
        msg = ws.receive()
        ws.send('Hello: '+msg)

if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), application=app, handler_class=WebSocketHandler)
    server.serve_forever()