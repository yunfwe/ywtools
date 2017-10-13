#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-21

from __future__ import absolute_import,print_function


dbConfig = {
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "123456",
    "db": "ywdb",
    "port": 3306,
    "charset": "utf8",
    "autocommit": True
}

class fieldMap(object):
    # 表名
    table       = 'ywdb.devices'
    # 下面是字段映射
    id          = 'id'              # 主键
    hostip      = 'ip_address'      # 主机IP
    ipmiip      = 'ipmi_address'    # IPMI接口IP
    ipmiUser    = 'ipmi_account'    # IDRAC登陆用户
    ipmiPass    = 'ipmi_passwd'     # IDRAC登陆密码
    status      = 'status'          # 0-OFF  1-ON  2-REBOOT  3-NULL
    position    = 'position'        # 所在机房位置
    # select限制
    limit = {'position':'北京'}


import time
import threading
import multiprocessing

import bottle
import socket
import pymysql
import setproctitle
setproctitle.setproctitle('idrac control center')
import dracclient.client
import urllib3;urllib3.disable_warnings()




class idrac(object):
    def __init__(self, ip, username, password):
        self.ip,self.username,self.password = ip,username,password
        self.client = dracclient.client.DRACClient(ip,username,password)

    def ping(self):
        # return True
        # try:
        #     return {'200':True}.get(str(requests.get(
        #         'https://{ip}/login.html'.format(ip=self.ip),
        #         verify=False,timeout=5).status_code),False)
        # except:
        #     return False
        s = socket.socket()
        if s.connect_ex((self.ip,443)) == 0:
            return True
        return False

    def getPowerState(self):
        try: return self.client.get_power_state()
        except Exception as e:
            print(str(e))
            return False

    def setPowerState(self,state):
        try:
            if self.client.set_power_state(state) is None:return True
            else: return False
        except: return False

# {'id':{'ip':'127.0.0.1','username':'root','password':'calvin','hostip':'127.0.0.1'}}
hostinfo = {}
_hostinfo = {}

# [(id,operation)] (1,'ON')  ON OFF REBOOT
process = []
processLock = threading.Lock()

tasks = []
tasksLock = threading.Lock()
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
        self.setName('Handler '+self.getName())
        self.tname = self.getName()
        with threadPoolLock: threadPool.append(self)

    def run(self):
        while True:
            if self.status == 'stop':
                print('exit...')
                with threadPoolLock: threadPool.remove(self)
                return
            self.status = 'pendding'
            self.setName(self.tname)
            try:
                with tasksLock:
                    task = tasks.pop()
                    print(task)
            except:
                # print('status: '+self.status)
                time.sleep(1)
                continue
            self.status = 'running'
            info = hostinfo.get(task[0])
            print(info)
            with processLock:process.append(task[0])
            self.setName('Handler Thread (%s)'%info['hostip'])
            cli = idrac(info['ipmiip'],info['username'],info['password'])
            time.sleep(10)
            ping = cli.ping()
            time.sleep(3)
            print(self.getName()+' run done')
            print(ping)    ####################
            if not ping:
                with rstLock: result.append((task[0],'connect error'))
                with processLock:process.remove(task[0])
                continue
            curstate = cli.getPowerState()
            print(curstate) #######################
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
                    with rstLock: result.append((task[0],'keep on'))
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
                    with rstLock: result.append((task[0],'keep off'))
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



def views(tasks):
    setproctitle.setproctitle('idrac web api')
    app = bottle.Bottle()
    @app.hook('after_request')
    def add_header():
        bottle.response.set_header('Access-Control-Allow-Origin','*')
        bottle.response.set_header('Access-Control-Allow-Method','*')

    field = ','.join([
        fieldMap.id,fieldMap.hostip, fieldMap.ipmiip,
        fieldMap.ipmiUser, fieldMap.ipmiPass, fieldMap.status
    ])
    table = fieldMap.table
    limit = fieldMap.position + '="' + fieldMap.limit['position']+'"'
    select_sql = "select {field} from {table} where {limit}".format(field=field,table=table,limit=limit)
    @app.route('/idrac/status/<id>')
    def idrac_status(id):
        if id == 'all':
            with pymysql.connect(**dbConfig) as db:
                global hostinfo
                global _hostinfo
                hostinfo = {}
                _hostinfo = {}
                for i in range(db.execute(select_sql)):
                    line = db.fetchone()
                    if not line[2]:continue
                    hostinfo[str(line[0])] = {'hostip':line[1],'ipmiip':line[2],'username':line[3],'password':line[4],'status':line[5]}
                    _hostinfo[str(line[0])] = {'hostip':line[1],'ipmiip':line[2],'status':line[5]}
            return _hostinfo
        else:
            return _hostinfo.get(id,{})
    if not hostinfo:idrac_status('all')


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
            # with tasksLock:
            #     for id in set(ids):
            #         tasks.append((str(id),option))
            for id in set(ids):
                tasks.put((str(id),option))
            return {"status":"ok","msg":"ok"}
        except:
            return {"status":"err","msg":"format error"}


    @app.route('/start/<num>')
    def start(num):
        for i in range(int(num)):
            HandlerThread().start()

    @app.route('/stop/<name>')
    def index(name):
        for i in threadPool:
            if i.getName() == name:
                i.status = 'stop'
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



    loop = list(range(100))
    @app.route('/loop')
    def v_loop():
        while True:
            time.sleep(1)
            try:
                yield str(loop.pop())+'\n'
            except IndexError:
                return 'done\n'

    @app.route('/echo')
    def echo():
        ws = bottle.request.environ.get('wsgi.websocket')
        while True:
            msg = ws.receive()
            ws.send('Hello: '+msg)


    def start():
        from gevent import monkey;monkey.patch_all()
        from gevent.pywsgi import WSGIServer
        from geventwebsocket.handler import WebSocketHandler
        server = WSGIServer(("0.0.0.0", 8080), application=app, handler_class=WebSocketHandler)
        server.serve_forever()

    start()


if __name__ == '__main__':
    viewProcess = multiprocessing.Process(target=views,args=(tasks,))
    viewProcess.start()
    # app.run(host='0.0.0.0')
    # main()