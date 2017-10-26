#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-16

# from __future__ import absolute_import, print_function

__version__ = '2.0.0'
__author__ = '魏云飞'


import os
import sys
import pwd
import time
import json
import queue
import random
import socket
import signal
import getopt
import logging
import threading

import bottle
import pymysql
import setproctitle
import dracclient.client
import urllib3

urllib3.disable_warnings()



class share(object):
    hostinfo = {}
    tasks = []
    tasksLock = threading.Lock()
    result = {}
    resultLock = threading.Lock()
    config = None


class HandlerProcess(object):
    taskQueue = queue.Queue()
    threadPool = []
    threadPoolLock = threading.Lock()

    def __init__(self):
        self.daemon = True

    class idrac(object):
        def __init__(self, ip, username, password):
            self.ip, self.username, self.password = ip, username, password
            self.client = dracclient.client.DRACClient(ip, username, password,
                ssl_retries=2,ready_retries=2,ready_retry_delay=1)

        def ping(self):
            # 如果对端443端口不能连接就不用继续进行了
            s = socket.socket()
            s.settimeout(1)
            if s.connect_ex((self.ip, 443)) == 0:
                return True
            return False

        def getPowerState(self):
            try:
                return self.client.get_power_state()
            except Exception as e:
                # print(str(e))
                return False

        def setPowerState(self, state):
            try:
                if self.client.set_power_state(state) is None:
                    return True
                else:
                    return False
            except Exception as e:
                # print(str(e))
                return False

    @staticmethod
    def dbupdate(id_, status):
        table = share.config['table']['name']
        field = share.config['table']['fieldmap']['status']
        idf = share.config['table']['fieldmap']['id']
        with pymysql.connect(**share.config['mysql']) as db:
            sql = '''update {table} set {field}="{status}" where {idf}="{i}"'''.format(
                table=table, field=field, status=status, idf=idf, i=id_
            )
            db.execute(sql)

    class HandlerThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.daemon = True
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
                if task == 'stop':
                    # print('exit...')
                    with HandlerProcess.threadPoolLock:
                        HandlerProcess.threadPool.remove(self)
                    return
                with share.resultLock:
                    share.result[task[2]] = {"status":"running","result":None}
                info = share.hostinfo.get(task[0])
                # print(task)
                if info is None:
                    with share.resultLock:
                        share.result[task[2]] = {"status":"stopped","result":"host not fonud"}
                        logging.error('ID: %s host not fonud' % task[0])
                    continue
                self.setName('Handler Thread (%s)' % info['hostip'])
                # print(self.name)
                self.status = 'running'
                # 开始实际的操作
                cli = HandlerProcess.idrac(info['ipmiip'], info['username'], info['password'])
                if not cli.ping():
                    with share.resultLock:
                        share.result[task[2]] = {"status":"stopped","result":"connect error"}
                        logging.error('Host: %s ipmi-%s connect error' % (info['hostip'],info['ipmiip']))
                    continue
                if task[1] == 'on':
                    if cli.setPowerState('POWER_ON'):
                        HandlerProcess.dbupdate(task[0], 'on')
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"on successful"}
                            logging.info('Host: %s on successful' % info['hostip'])
                        continue
                    else:
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"on failed"}
                            logging.error('Host: %s on failed' % info['hostip'])
                        continue
                if task[1] == 'off':
                    if cli.setPowerState('POWER_OFF'):
                        HandlerProcess.dbupdate(task[0], 'off')
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"off successful"}
                            logging.info('Host: %s off successful' % info['hostip'])
                        continue
                    else:
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"off failed"}
                            logging.error('Host: %s off failed' % info['hostip'])
                        continue
                if task[1] == 'reboot':
                    if cli.setPowerState('REBOOT'):
                        HandlerProcess.dbupdate(task[0], 'on')
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"reboot successful"}
                            logging.info('Host: %s reboot successful' % info['hostip'])
                        continue
                    else:
                        with share.resultLock:
                            share.result[task[2]] = {"status":"stopped","result":"reboot failed"}
                            logging.error('Host: %s reboot failed' % info['hostip'])
                        continue
                if task[1] == 'status':
                    status = cli.getPowerState()
                    if not status:
                        HandlerProcess.dbupdate(task[0], 'unknown')
                        with share.resultLock:
                            share.result[task[2]] = {"status": "finish","result":"cannot get status"}
                            logging.error('Host: %s cannot get status' % info['hostip'])
                        continue
                    if status == "POWER_ON":
                        HandlerProcess.dbupdate(task[0], 'on')
                        with share.resultLock:
                            share.result[task[2]] = {"status": "finish","result":"power on"}
                            logging.info('Host: %s is power on' % info['hostip'])
                        continue
                    if status == "POWER_OFF":
                        HandlerProcess.dbupdate(task[0], 'off')
                        with share.resultLock:
                            share.result[task[2]] = {"status": "finish","result": "power off"}
                            logging.info('Host: %s is power off' % info['hostip'])
                        continue
                    if status == "REBOOT":
                        HandlerProcess.dbupdate(task[0], 'on')
                        with share.resultLock:
                            share.result[task[2]] = {"status": "finish","result": "power reboot"}
                            logging.info('Host: %s is power reboot' % info['hostip'])
                        continue

    class TasksManagerThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.daemon = True
            self.status = 'start'
            self.setName('Tasks Manager Thread')
            with HandlerProcess.threadPoolLock:
                HandlerProcess.threadPool.append(self)

        def run(self):
            while True:
                with share.tasksLock:
                    num = len(share.tasks)
                    if num != 0:
                        while num > 0:
                            HandlerProcess.taskQueue.put(share.tasks.pop())
                            num -= 1
                time.sleep(1)

    @staticmethod
    def run():
        HandlerProcess.TasksManagerThread().start()
        for i in range(int(share.config['daemon']['threads'])):
            HandlerProcess.HandlerThread().start()


class WebManageProcess(object):
    def __init__(self):
        self.daemon = True

    @staticmethod
    def mkstr(size=8):
        pool = list(range(97, 123)) + list(range(65, 91)) + list(range(48, 58))
        _str = ''
        for i in range(size):
            _str += chr(random.choice(pool))
        return _str

    @staticmethod
    def sqlparse():
        val = share.config['table']['fieldmap']
        field = ','.join([
            val['id'], val['hostip'], val['ipmiip'],
            val['ipmiuser'], val['ipmipass'], val['status'], val['position']
        ])
        table = share.config['table']['name']

        def limitparse():
            _limit = share.config['table'].get('limit')
            limits = ''
            if not _limit: return ''
            _tmp = []
            for k, v in _limit.items():
                if type(v) == str:
                    v = '"' + v + '"'
                else:
                    v = str(v)
                _tmp.append(k + '=' + v)
            if not _tmp: limits = ''
            if len(_tmp) == 1: limits = ' where ' + _tmp[0]
            if len(_tmp) > 1: limits = ' where ' + ' and '.join(_tmp)
            return limits

        limit = limitparse()
        sql = 'select ' + field + ' from ' + table + limit
        return sql

    @staticmethod
    def webapi():
        app = bottle.Bottle()

        @app.hook('after_request')
        def add_header():
            """
            浏览器请求跨域处理
            """
            bottle.response.set_header('Access-Control-Allow-Origin', '*')
            bottle.response.set_header('Access-Control-Allow-Methods', '*')
            bottle.response.set_header('Access-Control-Allow-Headers', "Content-Type")


        @app.route('/thread/list')
        def thread_list():
            for i in HandlerProcess.threadPool:
                yield i.name+'\t\t('+i.status+')\n'

        @app.route('/thread/add/<num>')
        def thread_add(num):
            for i in range(int(num)):
                HandlerProcess.HandlerThread().start()

        @app.route('/thread/stop/<num>')
        def thread_stop(num):
            threadnum = len(HandlerProcess.threadPool)-1
            if num == 'all':
                num = threadnum
            num = int(num)
            if num > threadnum:
                num = threadnum
            for i in range(num):
                with share.tasksLock:
                    share.tasks.append('stop')

        @app.route('/result/show')
        def result_show():
            with share.resultLock:
                return share.result

        @app.route('/result/clean')
        def result_clean():
            with share.resultLock:
                share.result = {}

        loop = list(range(1000))
        @app.route('/loop')
        def _loop():
            while True:
                time.sleep(1)
                try:
                    yield str(loop.pop()) + '\n'
                except IndexError:
                    return 'done\n'

        @app.route('/idrac/info/<ip>', method=['GET'])
        def idrac_status(ip):
            """
            根据IP查询信息
            如果IP的值为all 则返回所有检索到的信息
            """
            if ip == 'all':
                _hostinfo = {}
                with pymysql.connect(**share.config['mysql']) as db:
                    for i in range(db.execute(WebManageProcess.sqlparse())):
                        line = db.fetchone()
                        if not line[2]: continue
                        share.hostinfo[str(line[0])] = {'hostip': line[1], 'ipmiip': line[2],
                                                                   'username': line[3],
                                                                   'password': line[4], 'status': line[5],
                                                                   'position': line[6]}
                        _hostinfo[str(line[0])] = {'hostip': line[1], 'ipmiip': line[2], 'status': line[5],
                                                  'position': line[6]}
                return json.dumps(_hostinfo, ensure_ascii=False)
            else:
                sql = WebManageProcess.sqlparse()
                if 'where' in sql:
                    sql = sql + ' and ' + share.config['table']['fieldmap']['hostip'] + '="' + ip + '"'
                else:
                    sql = sql + ' where ' + share.config['table']['fieldmap']['hostip'] + '="' + ip + '"'
                with pymysql.connect(**share.config['mysql']) as db:
                    l = db.execute(sql)
                    if l == 1:
                        line = db.fetchone()
                        return json.dumps({'id': str(line[0]), 'hostip': line[1], 'ipmiip': line[2], 'status': line[5],
                                           'position': line[6]}, ensure_ascii=False)
                    else:
                        return {}

        if not share.hostinfo: idrac_status('all')

        @app.route('/idrac/control/async', method=['POST','OPTIONS'])
        def idrac_control_async():
            """
            接受 {"id":[1,2,3,4],"action":"on"} 或者 {"id":1,"action":"on"} 的json格式
            content-type： application/json
            此函数异步执行 不返回执行结果 只返回数据是否成功放入任务队列
            任务的处理结果会直接更改数据库
            可以执行 "on","off","reboot" 操作

            因为接受的参数是根据id 所以对人并不友好 用于浏览器发起请求
            """
            try:
                ids = bottle.request.json.get('id')
                action = bottle.request.json.get('action').lower()
                if action not in ["on", "off", "reboot", "status"]: return {"status": "error", "result": "error action"}
                taskid = []
                if type(ids) != list:
                    with share.tasksLock:
                        _taskid = WebManageProcess.mkstr()
                        share.tasks.append((str(ids), action, _taskid))
                        taskid.append({str(ids):_taskid})
                else:
                    with share.tasksLock:
                        for _id in set(ids):
                            _taskid = WebManageProcess.mkstr()
                            share.tasks.append((str(_id), action, _taskid))
                            taskid.append({str(_id):_taskid})
                # print(share.tasks)
                return {"status": "ok","taskid":taskid}
            except Exception as e:
                return {"status": "err", "result": str(e)}

        @app.route('/idrac/result/<taskid>', method=['GET'])
        def idrac_result(taskid):
            try:
                return share.result.pop(taskid)
            except KeyError:
                return {}
            # return share.result.get(taskid,{})

        @app.route('/idrac/control/sync', method=['POST','OPTIONS'])
        def idrac_control_sync():
            """
            接受 {"id":1,"action":"on"} 的json格式
            content-type： application/json
            同步执行 会直接返回执行结果
            可以执行 "on","off","reboot","status" 操作

            因为接受的参数是根据id 所以对人并不友好 用于浏览器发起请求
            """
            try:
                _id = str(bottle.request.json.get('id'))
                action = bottle.request.json.get('action').lower()
                if action not in ["on", "off", "reboot", "status"]:
                    return {"status": "error", "result": "error action"}
                info = share.hostinfo.get(_id)
                if info is None:
                    logging.error('ID: %s host not fonud' % _id)
                    return {"status": "error", "result": "host not found"}
                cli = HandlerProcess.idrac(ip=info['ipmiip'], username=info['username'], password=info['password'])
                if not cli.ping():
                    logging.error('Host: %s ipmi-%s connect error' % (info['hostip'],info['ipmiip']))
                    return {"status": "error", "result": "connect error"}
                if action == 'on':
                    if cli.setPowerState('POWER_ON'):
                        HandlerProcess.dbupdate(_id, 'on')
                        logging.info('Host: %s on successful' % info['hostip'])
                        return {"status": "ok", "result": "on successful"}
                    logging.error('Host: %s on failed' % info['hostip'])
                    return {"status": "error", "result": "on failed"}
                if action == 'off':
                    if cli.setPowerState('POWER_OFF'):
                        HandlerProcess.dbupdate(_id, 'off')
                        logging.info('Host: %s off successful' % info['hostip'])
                        return {"status": "ok", "result": "off successful"}
                    logging.error('Host: %s off failed' % info['hostip'])
                    return {"status": "error", "result": "off failed"}
                if action == 'reboot':
                    if cli.setPowerState('REBOOT'):
                        HandlerProcess.dbupdate(_id, 'on')
                        logging.info('Host: %s reboot successful' % info['hostip'])
                        return {"status": "ok", "result": "reboot successful"}
                    logging.error('Host: %s reboot failed' % info['hostip'])
                    return {"status": "error", "result": "reboot failed"}
                if action == 'status':
                    status = cli.getPowerState()
                    if not status:
                        logging.error('Host: %s cannot get status' % info['hostip'])
                        HandlerProcess.dbupdate(_id, 'unknown')
                        return {"status": "error", "result": "cannot get status"}
                    if status == "POWER_ON":
                        logging.info('Host: %s is power on' % info['hostip'])
                        HandlerProcess.dbupdate(_id, 'on')
                        return {"status": "ok","result":"power on"}
                    if status == "POWER_OFF":
                        logging.info('Host: %s is power off' % info['hostip'])
                        HandlerProcess.dbupdate(_id, 'off')
                        return {"status": "ok","result": "power off"}
                    if status == "REBOOT":
                        logging.info('Host: %s is power reboot' % info['hostip'])
                        HandlerProcess.dbupdate(_id, 'on')
                        return {"status": "ok","result": "power reboot"}
            except Exception as e:
                logging.error(str(e))
                return {"status": "error", "result": str(e)}

        @app.route('/idrac/<action>/<ip>', method=['GET'])
        def simple_control(action, ip):
            """
            对用户友好的接口 可以直接使用浏览器或者curl等工具访问
            不应用配置文件中的limit
            """
            try:
                if action not in ["on", "off", "reboot", "status"]: return "仅支持 on/off/reboot/status 操作\n"
                val = share.config['table']['fieldmap']
                field = ','.join([val['id'], val['ipmiip'], val['ipmiuser'], val['ipmipass']])
                table = share.config['table']['name']
                # info = None
                sql = 'select {field} from {table} where {host}="{ip}"'.format(
                    field=field, table=table, host=val['hostip'], ip=ip)
                with pymysql.connect(**share.config['mysql']) as db:
                    line = db.execute(sql)
                    if line != 1:
                        logging.error('Host: %s can not found' % ip)
                        return "IP地址查询有误 请检查数据库是否存在此IP 或者此IP记录是否只有一条\n"
                    info = db.fetchone()
                _id = str(info[0])
                cli = HandlerProcess.idrac(ip=info[1], username=info[2], password=info[3])
                if not cli.ping():
                    logging.error('Host: %s ipmi-%s connect error' % (ip,info[1]))
                    return "连接此IDRAC失败\n"
                if action == 'on':
                    if cli.setPowerState('POWER_ON'):
                        HandlerProcess.dbupdate(_id, 'on')
                        logging.info('Host: %s on successful' % ip)
                        return "主机：%s 启动成功\n" % ip
                    logging.error('Host: %s on failed' % ip)
                    return "主机：%s 启动失败\n" % ip
                if action == 'off':
                    if cli.setPowerState('POWER_OFF'):
                        HandlerProcess.dbupdate(_id, 'off')
                        logging.info('Host: %s off successful' % ip)
                        return "主机：%s 关闭成功\n" % ip
                    logging.error('Host: %s off failed' % ip)
                    return "主机：%s 关闭失败\n" % ip
                if action == 'reboot':
                    if cli.setPowerState('REBOOT'):
                        HandlerProcess.dbupdate(_id, 'on')
                        logging.info('Host: %s reboot successful' % ip)
                        return "主机：%s 重启成功\n" % ip
                    logging.error('Host: %s reboot failed' % ip)
                    return "主机：%s 重启失败\n" % ip
                if action == 'status':
                    status = cli.getPowerState()
                    if not status:
                        logging.error('Host: %s cannot get status' % ip)
                        HandlerProcess.dbupdate(_id, 'unknown')
                        return "主机：%s 状态获取失败\n" % ip
                    if status == "POWER_ON":
                        logging.info('Host: %s is power on' % ip)
                        HandlerProcess.dbupdate(_id, 'on')
                        return "主机：%s 已开机\n" % ip
                    if status == "POWER_OFF":
                        logging.info('Host: %s is power off' % ip)
                        HandlerProcess.dbupdate(_id, 'off')
                        return "主机：%s 已关机\n" % ip
                    if status == "REBOOT":
                        logging.info('Host: %s is power reboot' % ip)
                        HandlerProcess.dbupdate(_id, 'on')
                        return "主机：%s 正在重启\n" % ip
            except Exception as e:
                logging.error(str(e))
                return "抱歉 服务端出错了\n详情: " + str(e) + '\n'

        return app

    @staticmethod
    def run():
        from gevent import monkey; monkey.patch_time()
        from gevent.pywsgi import WSGIServer
        from geventwebsocket.handler import WebSocketHandler
        bind = (share.config['web']['listen'], share.config['web']['port'])
        app = WebManageProcess.webapi()
        server = WSGIServer(bind, application=app, handler_class=WebSocketHandler)
        print('[PID: %s] Server listen on %s:%s ...' % (os.getpid(), bind[0],bind[1]))
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


def daemon():
    os.setegid(pwd.getpwnam(share.config['daemon']['group']).pw_gid)
    os.seteuid(pwd.getpwnam(share.config['daemon']['user']).pw_uid)
    setproctitle.setproctitle('idrac_daemon_process')

    # 杀死进程的方法 然后捕获SIGTERM信号
    def killsubprocess(sig_num, addtion):
        del sig_num, addtion
        print('IDRAC Manager Exit...')
        os.kill(os.getpid(), 9)

    signal.signal(signal.SIGTERM, killsubprocess)

    HandlerProcess.run()
    WebManageProcess.run()


def optparse():
    CONFIG = {
        "daemon": {
            "threads": 10,
            "user": "nobody",
            "group": "nobody",
            "log": "/tmp/idracManager.log",
            "log-level": "info"
        },
        "web": {
            "listen": "0.0.0.0",
            "port": 11190
        },
        "mysql": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "123456",
            "db": "ywdb",
            "charset": "utf8",
            "autocommit": True
        },
        "table": {
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
        'POWER_ON': 'on',
        'REBOOT': 'reboot'
    }

    loglevel = {
        'debug': 10,
        'info': 20,
        'warning': 30,
        'error': 40,
        'caitical': 50
    }

    try:
        options = getopt.getopt(sys.argv[1:], 'vhdc:i:u:p:a:t:', ['config-template'])
    except getopt.GetoptError as e:
        print(str(e) + '. Use -h see more.')
        sys.exit(255)
    if not options[0] and not options[1]:
        usage()

    def hasops(ops):
        return dict(options[0]).get(ops, False)

    for name, value in options[0]:
        if name == '-h':
            usage()
        if name == '-v':
            print('版本: ' + __version__)
            print('作者: ' + __author__)
            sys.exit(0)
        if name == '--config-template':
            print(json.dumps(CONFIG, indent=4, ensure_ascii=False))
            print()
            sys.stderr.write('注意：daemon中threads的值为启动时开启的工作线程 批量开关机中 工作线程越多 并发越大\n')
            sys.exit(0)
        if name == '-c':
            if hasops('-d') == '':
                pid = os.fork()
                if pid != 0: sys.exit(0)
            share.config = json.load(open(value))
            logging.basicConfig(level=loglevel.get(share.config['daemon']['log-level'],20),
                                format='%(asctime)s [idracManager] %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=share.config['daemon']['log'],
                                filemode='a')
            daemon()
        if name == '-i':
            if not hasops('-a'):
                print('必须使用 -a 指定要进行的操作: on/off/reboot')
                sys.exit(2)
            ipmiinfo['ip'] = value
            continue
        if name == '-u':
            if not hasops('-i'):
                print('必须使用 -i 指定IDRAC的IP地址')
                sys.exit(2)
            ipmiinfo['username'] = value
            continue
        if name == '-p':
            if not hasops('-i'):
                print('必须使用 -i 指定IDRAC的IP地址')
                sys.exit(2)
            ipmiinfo['password'] = value
            continue
        if name == '-a':
            if hasops('-t'):
                def kill(timeout):
                    time.sleep(timeout)
                    print('等待超时 程序正在退出...')
                    # 发送SIGINT信号 相当于Ctrl+C
                    os.kill(os.getpid(), 2)
                    time.sleep(0.1)

                threading.Thread(target=kill, args=(int(hasops('-t')),), daemon=True).start()
            cli = HandlerProcess.idrac(**ipmiinfo)
            if not cli.ping():
                print("IDRAC: %s 无法连接" % ipmiinfo['ip'])
                sys.exit(1)
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
                print('IDRAC: %s   %s' % (ipmiinfo['ip'].ljust(15), power.get(cli.getPowerState())))
            else:
                print('无效的操作: %s' % value)
                sys.exit(1)


if __name__ == '__main__':
    try:
        optparse()
    except KeyboardInterrupt:
        os.kill(os.getpid(), 15)
    except Exception as e:
        print(str(e))
        sys.exit(1)
