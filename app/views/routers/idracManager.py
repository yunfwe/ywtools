#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-11

from __future__ import absolute_import, print_function

__version__ = '1.0.0'
__author__ = '魏云飞'


import os
import sys
import pwd
import time
import json
import queue
import socket
import signal
import getopt
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
                # 开始实际的操作

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


def usage():
    print("戴尔远程管理卡命令行工具\n"
            "\n"
            "    -v                  显示版本\n"
            "    -h                  显示此帮助\n"
            "\n"
            "    后端模式运行程序\n"
            "    -d                  守护进程模式 如果没有此参数 将在前台运行\n"
            "    -c                  指定配置文件路径\n"
            "    --config-template   生成配置文件模板\n"
            "\n"
            "    命令行方式运行程序\n"
            "    -i                  IDRAC地址\n"
            "    -u                  IDRAC登陆用户\n"
            "    -p                  IDRAC用户密码\n"
            "    -a                  所要执行的操作 仅支持 on/off/reboot/status  [开机/关机/重启/状态]\n"
            "    -t                  等待超时 超时后将自动停止进程\n")
    sys.exit(255)



def daemon(config):
    setproctitle.setproctitle('idrac: Communication Process')
    os.setegid(pwd.getpwnam('nobody').pw_gid)
    os.seteuid(pwd.getpwnam('nobody').pw_uid)
    man = multiprocessing.Manager()
    # {'id':{'ip':'127.0.0.1','username':'root','password':'calvin','hostip':'127.0.0.1'}}
    hostinfo = man.dict()
    tasks = man.list()
    tasksLock = man.Lock()
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
        print('IDRAC Manager Exit...')

    signal.signal(signal.SIGTERM, killsubprocess)

    # 父进程(Daemon) 等待两个子进程
    H.join()
    W.join()

def optparse():
    CONFIG = {
        "daemon": {
            "threads": 10,
        },
        "web":{
            "listen":"0.0.0.0",
            "port": 8080
        },
        "mysql":{
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "123456",
            "db": "ywdb",
            "charset": "utf8",
            "autocommit": True
        },
        "table":{
            "name": "devices",
            "fieldmap": {
                "id": "id",
                "hostip": "ip_address",
                "ipmiip": "ipmi_address",
                "ipmiuser": "ipmi_account",
                "ipmipass": "ipmi_passwd",
                "status": "status",
                "position": "position",
            },
            "limit": {
                "position": "北京"
            }
        }
    }
    ipmiinfo = {
        'ip': None,
        'username': 'root',
        'password': 'calvin',
    }

    power = {
        'POWER_OFF': 'off',
        'POWER_ON' : 'on',
        'REBOOT'   : 'reboot'
    }

    try:
        options = getopt.getopt(sys.argv[1:], 'vhdc:i:u:p:a:t:', ['config-template'])
    except getopt.GetoptError as e:
        print(str(e) + '. Use -h see more.')
        sys.exit(255)
    if not options[0] and not options[1]:
        usage()

    def hasops(ops):
        return dict(options[0]).get(ops,False)

    for name,value in options[0]:
        if name == '-h':
            usage()
        if name == '-v':
            print('版本: '+__version__)
            print('作者: '+__author__)
            sys.exit(0)
        if name == '--config-template':
            print(json.dumps(CONFIG,indent=4))
            print()
            sys.stderr.write('注意：daemon中threads的值为启动时开启的工作线程 批量开关机中 工作线程越多 并发越大\n')
            sys.exit(0)
        if name == '-c':
            if hasops('-d') == '':
                pid = os.fork()
                if pid != 0:sys.exit(0)
            CONFIG = json.load(open(value))
            daemon(CONFIG)
        if name == '-i':
            if not hasops('-a'):
                print('必须使用 -a 指定要进行的操作: on/off/reboot')
                sys.exit(2)
            ipmiinfo['ip'] = value;continue
        if name == '-u':
            if not hasops('-i'):
                print('必须使用 -i 指定IDRAC的IP地址')
                sys.exit(2)
            ipmiinfo['username'] = value;continue
        if name == '-p':
            if not hasops('-i'):
                print('必须使用 -i 指定IDRAC的IP地址')
                sys.exit(2)
            ipmiinfo['password'] = value;continue
        if name == '-a':
            if hasops('-t'):
                def kill(timeout):
                    time.sleep(timeout)
                    print('等待超时 程序正在退出...')
                    # 发送SIGINT信号 相当于Ctrl+C
                    os.kill(os.getpid(),2)
                    time.sleep(0.1)
                threading.Thread(target=kill,args=(int(hasops('-t')),),daemon=True).start()
            cli = HandlerProcess.idrac(**ipmiinfo)
            # if not cli.ping():
            #     print("IDRAC: %s 无法连接" % ipmiinfo['ip'])
            #     sys.exit(1)
            if value.lower() == 'on':
                if cli.setPowerState('POWER_ON'):
                    print('IDRAC: %s      on  \033[32msuccess\033[0m' % ipmiinfo['ip'].ljust(15))
                else:
                    print('IDRAC: %s      on  \033[31mfailed\033[0m' % ipmiinfo['ip'].ljust(15))
            elif value.lower() == 'off':
                if cli.setPowerState('POWER_OFF'):
                    print('IDRAC: %s      off  \033[32msuccess\033[0m' % ipmiinfo['ip'].ljust(15))
                else:
                    print('IDRAC: %s      off  \033[31mfailed\033[0m' % ipmiinfo['ip'].ljust(15))
            elif value.lower() == 'reboot':
                if cli.setPowerState('REBOOT'):
                    print('IDRAC: %s      reboot  \033[32msuccess\033[0m' % ipmiinfo['ip'].ljust(15))
                else:
                    print('IDRAC: %s      reboot  \033[31mfailed\033[0m' % ipmiinfo['ip'].ljust(15))
            elif value.lower() == 'status':
                print('IDRAC: %s   %s'%(ipmiinfo['ip'].ljust(15),power.get(cli.getPowerState())))
            else:
                print('无效的操作: %s' % value)
                sys.exit(1)




if __name__ == '__main__':
    try:
        optparse()
    except KeyboardInterrupt:
        os.kill(os.getpid(),15)
    except Exception as e:
        print(str(e))
        sys.exit(1)
