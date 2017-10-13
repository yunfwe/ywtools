#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-11

from __future__ import absolute_import, print_function

import os
import sys
import pwd
import time
import queue
import socket
import signal
import threading
import multiprocessing

import bottle
import pymysql
import setproctitle
import dracclient.client
import urllib3

urllib3.disable_warnings()


class HandlerProcess(multiprocessing.Process):
    threadPool = []
    threadPoolLock = threading.Lock()
    hostinfo = {}
    tasks = []
    tasksLock = None
    taskQueue = queue.Queue()

    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True

    class idrac(object):
        def __init__(self, ip, username, password):
            self.ip, self.username, self.password = ip, username, password
            self.client = dracclient.client.DRACClient(ip, username, password)

        def ping(self):
            # 如果对端443端口不能连接就不用继续进行了
            s = socket.socket()
            if s.connect_ex((self.ip, 443)) == 0:
                return True
            return False

        def getPowerState(self):
            try:
                return self.client.get_power_state()
            except Exception as e:
                print(str(e))
                return False

        def setPowerState(self, state):
            try:
                if self.client.set_power_state(state) is None:
                    return True
                else:
                    return False
            except:
                return False

    class HandlerThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.status = 'start'
            self.setName('Handler ' + self.getName())
            self.ThreadName = self.getName()
            with HandlerProcess.threadPoolLock:
                HandlerProcess.threadPool.append(self)

        def run(self):
            while True:
                self.status = 'pendding'
                self.setName(self.ThreadName)
                task = HandlerProcess.taskQueue.get()
                print(self.ThreadName + task)
                if task == 'stop':
                    print('exit...')
                    with HandlerProcess.threadPoolLock:
                        HandlerProcess.threadPool.remove(self)
                    return
                self.status = 'running'

    def run(self):
        setproctitle.setproctitle('idrac: Handler Process')
        os.setegid(pwd.getpwnam('nobody').pw_gid)
        os.seteuid(pwd.getpwnam('nobody').pw_uid)
        for i in range(10):
            HandlerProcess.HandlerThread().start()
        while True:
            with HandlerProcess.tasksLock:
                num = len(HandlerProcess.tasks)
                if num != 0:
                    while num > 0:
                        HandlerProcess.taskQueue.put(HandlerProcess.tasks.pop())
                        num -= 1
            time.sleep(1)


class WebManageProcess(multiprocessing.Process):
    hostinfo = {}
    tasks = []
    tasksLock = None

    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True

    @staticmethod
    def database():
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
            table = 'ywdb.devices'
            # 下面是字段映射
            id = 'id'  # 主键
            hostip = 'ip_address'  # 主机IP
            ipmiip = 'ipmi_address'  # IPMI接口IP
            ipmiUser = 'ipmi_account'  # IDRAC登陆用户
            ipmiPass = 'ipmi_passwd'  # IDRAC登陆密码
            status = 'status'  # 0-OFF  1-ON  2-REBOOT  3-NULL
            position = 'position'  # 所在机房位置
            # select限制
            limit = {'position': '北京'}

    @staticmethod
    def webapi():
        app = bottle.Bottle()

        @app.hook('after_request')
        def add_header():
            bottle.response.set_header('Access-Control-Allow-Origin', '*')
            bottle.response.set_header('Access-Control-Allow-Method', '*')

        @app.route('/put/<name>')
        def put(name):
            yield 'wait...\n'
            time.sleep(3)
            with WebManageProcess.tasksLock:
                WebManageProcess.tasks.append(name)
            time.sleep(3)
            yield 'done...\n'

        return app

    def run(self):
        setproctitle.setproctitle('idrac: Web Manage Process')
        os.setegid(pwd.getpwnam('nobody').pw_gid)
        os.seteuid(pwd.getpwnam('nobody').pw_uid)
        from gevent import monkey;monkey.patch_all(socket=False)
        from gevent.pywsgi import WSGIServer
        from geventwebsocket.handler import WebSocketHandler
        server = WSGIServer(("0.0.0.0", 8080), application=WebManageProcess.webapi(), handler_class=WebSocketHandler)
        server.serve_forever()


def main():
    # 初始化处理进程和web管理进程
    setproctitle.setproctitle('idrac: Daemon Process')
    HandlerProcess.hostinfo = hostinfo
    HandlerProcess.tasks = tasks
    HandlerProcess.tasksLock = tasksLock
    H = HandlerProcess()
    WebManageProcess.hostinfo = hostinfo
    WebManageProcess.tasks = tasks
    WebManageProcess.tasksLock = tasksLock
    W = WebManageProcess()

    # 启动这两个进程
    H.start()
    W.start()

    # 杀死子进程的方法 然后捕获SIGTERM信号
    def killsubprocess(sig_num, addtion):
        del sig_num, addtion
        H.terminate()
        W.terminate()

    signal.signal(signal.SIGTERM, killsubprocess)

    # 父进程(Daemon) 等待两个子进程
    H.join()
    W.join()


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'daemon':
            pid = os.fork()
            if pid != 0: sys.exit(0)
    except IndexError:
        pass
    setproctitle.setproctitle('idrac: Communication Process')
    os.setegid(pwd.getpwnam('nobody').pw_gid)
    os.seteuid(pwd.getpwnam('nobody').pw_uid)
    man = multiprocessing.Manager()
    # {'id':{'ip':'127.0.0.1','username':'root','password':'calvin','hostip':'127.0.0.1'}}
    hostinfo = man.dict()
    tasks = man.list()
    tasksLock = man.Lock()
    try:
        main()
    except KeyboardInterrupt:
        print('Operation cancelled by user')
        sys.exit(0)
