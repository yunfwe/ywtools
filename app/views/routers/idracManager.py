#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-11

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


import os
import sys
import pwd
import time
import signal
import threading
import multiprocessing

import bottle
import socket
import pymysql
import setproctitle
setproctitle.setproctitle('idrac: Daemon Process')
import dracclient.client
import urllib3;urllib3.disable_warnings()


class HandlerProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True

    class idrac(object):
        def __init__(self, ip, username, password):
            self.ip,self.username,self.password = ip,username,password
            self.client = dracclient.client.DRACClient(ip,username,password)

        def ping(self):
            # 如果对端443端口不能连接就不用继续进行了
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

    class HandlerThread(threading.Thread):pass

    def run(self):
        setproctitle.setproctitle('idrac: Handler Process')
        os.setegid(pwd.getpwnam('nobody').pw_gid)
        os.seteuid(pwd.getpwnam('nobody').pw_uid)
        time.sleep(1000)

class WebManageProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True
    def run(self):
        setproctitle.setproctitle('idrac: Web Manage Process')
        os.setegid(pwd.getpwnam('nobody').pw_gid)
        os.seteuid(pwd.getpwnam('nobody').pw_uid)
        time.sleep(1000)


try:
    if __name__ == '__main__':
        try:
            if sys.argv[1] == 'daemon':
                pid = os.fork()
                if pid != 0: sys.exit(0)
        except IndexError:pass
        H = HandlerProcess()
        W = WebManageProcess()
        H.start()
        W.start()
        def term(sig_num, addtion):
            del sig_num,addtion
            H.terminate()
            W.terminate()
        signal.signal(signal.SIGTERM, term)
        H.join()
        W.join()
except KeyboardInterrupt:
    print('Operation cancelled by user')
    sys.exit(0)







