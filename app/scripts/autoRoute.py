#!/usr/bin/python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-05-23

import re
import os
import time
import json
import socket
import threading
from commands import getstatusoutput as cmd

ppp0used = False
netMonitorStart = False
timeThread = False
ethUsed = False
ethcanUsed = False
reconnectCount = 0

DEBUG = False

def updateDNS():
    open('/etc/ppp/resolv.conf','w').close()
    open('/etc/resolvconf/resolv.conf.d/tail','w').close()
    open('/etc/resolvconf/resolv.conf.d/head','w').close()
    os.popen("sed -i 's/^usepeerdns/#usepeerdns/g' /etc/ppp/peers/wcdma").read()
    os.popen("sed -i 's/^usepeerdns/#usepeerdns/g' /etc/ppp/peers/provider").read()
    open('/etc/resolv.conf','w').write('nameserver 223.6.6.6\nnameserver 180.76.76.76\n')

updateDNS()

# 网络监控线程
class netMonitor(threading.Thread):
    def __init__(self):
        super(netMonitor, self).__init__()
        self.failedCount = 0
        self.daemon = True
        self.name = 'netMonitor'
        self.logPath = '/var/log/autoRoute-netMonitor.log'
        f =  open('/usr/local/wwwl/wtwatcher/config.xml').read()
        try:
            #raise Exception()    # 默认使用直接连接服务器端口的方法，如果想使用ping就解除这句话的注释
            data = re.findall(r'<superior>(.*?)</superior>',f)
            ip,port = data[0].split(':')
            self.target = ip,int(port)
        except:
            ip = socket.getaddrinfo('4g.jjtrobot.com',None)[0][-1][0]
            self.target = ip
        self.logReboot = lambda msg:open('/var/log/autoRoute-reboot.log','a').write(
            time.strftime('[%Y-%m-%d %H:%M:%S] ')+'rebooting %s...\n' % msg)

    def log(self):
        logFormat = {
            "time":time.strftime('%Y-%m-%d %H:%M:%S'),
            "interface":None,"ping":None, "route":None
        }
        logFormat['interface'] = netMonitor.getInterface()
        if len(self.target) == 2:
            logFormat['ping'] = self.connect()
        else:
            logFormat['ping'] = self.ping()
        logFormat['route'] = netMonitor.getRoute()
        open(self.logPath,'ab').write(
            json.dumps(logFormat)+'\n'
        )

    @staticmethod
    def getInterface():
        interface = [x.split(':')[0].strip() for x in open('/proc/net/dev').readlines()[2:]]
        interface = list(set(interface) - set(['lo','can0']))
        result = ''
        for i in interface:
            result += os.popen('ifconfig %s |grep -E  "Link|inet |RX bytes"' % i).read()
        return result

    @staticmethod
    def getRoute():
        return os.popen('ip ro show').read()

    def ping(self):
        status,output = cmd("ping %s -c5 -W5 -i0.2" % self.target)
        if status == 0:
            self.failedCount  = 0
        else:
            self.failedCount  += 1
        return '\n'.join(output.split('\n')[-3:])+' failedCount='+str(self.failedCount)

    def connect(self):
        s = socket.socket()
        s.settimeout(10)
        try:
            s.connect(self.target)
            self.failedCount = 0
            s.close()
            return 'Connect %s:%s success! failedCount=%s' % (self.target[0],self.target[1],self.failedCount)
        except Exception:
            s.close()
            self.failedCount += 1
            return 'Connect %s:%s failed! failedCount=%s' % (self.target[0],self.target[1],self.failedCount)

    @staticmethod
    def restartNetwork():
        os.popen('killall pppd').read()

    def run(self):
        global ethcanUsed
        while True:
            if ethcanUsed:
                time.sleep(10)
                continue
            self.log()
            if self.failedCount == 720:      # 720 * 120 = 超过1天没连接到服务器就重启系统
                self.logReboot('system')
                os.popen('reboot').read()
            elif self.failedCount%5 == 0:     # 5 * 120 = 每10分钟没连接服务器就重启4G拨号
                if self.failedCount != 0:
                    self.logReboot('ppp0')
                    netMonitor.restartNetwork()
            time.sleep(120) # 两分钟采集一次数据 每次数据大约1K左右 一年500M左右的日志大小

# 时间同步线程
def timeSync():
    global ppp0used,netMonitorStart
    while True:
        log('timeSync...')
        os.popen('ntpdate 182.92.12.11').read()
        time.sleep(3600) # 每小时同步一次

def log(msg):
    now = time.strftime('[%Y/%m/%d %H:%M:%S] ')
    open('/var/log/autoRoute.log','a').write(now+msg+'\n')

flushRoute = lambda : os.popen('ip ro flush cache').read()

getDefRoutes = lambda :[x for x in os.popen('ip ro show').read().split('\n') if x[:7]=='default']

hasppp0 = lambda :'ppp0:' in open('/proc/net/dev').read().split()

os.popen('sysctl net.ipv4.ip_forward=1').read()
if 'test' not in open('/etc/iproute2/rt_tables').read().split():
    open('/etc/iproute2/rt_tables','a',buffering=0).write('\n11\ttest\n')

def delDefRoutes():
    for r in getDefRoutes():
        os.popen('ip ro del '+r).read()
    flushRoute()

def getEthRoute():
    return [x for x in open('/etc/network/interfaces') if x.strip()[:7] == 'gateway'][0].split()[-1]

gateway = getEthRoute()

def initRouteTable():
    global gateway
    # 腾讯公共DNS作为测试IP
    os.popen('ip ru del from 119.29.29.29 lookup test').read()
    os.popen('ip ru del to 119.29.29.29 lookup test').read()
    os.popen('ip ru add from 119.29.29.29 lookup test').read()
    os.popen('ip ru add to 119.29.29.29 lookup test').read()
    os.popen('ip ro replace default via '+gateway+' dev eth0 table test').read()
    flushRoute()

def switchToEth():
    delDefRoutes()
    os.popen('ip ro add default via '+gateway+' dev eth0').read()
    flushRoute()
    os.popen('bash -c "/etc/init.d/wtlar-service restart"')

def switchTo4G():
    delDefRoutes()
    os.popen('ip ro add default dev ppp0').read()
    flushRoute()
    os.popen('bash -c "/etc/init.d/wtlar-service restart"')

def connect4G():
    global ethcanUsed
    global reconnectCount
    while True:
        if not ethcanUsed:
            os.popen('pppd call wcdma').read()
            reconnectCount += 1
            if reconnectCount > 20:
                time.sleep(300)
                reconnectCount = 0
            elif reconnectCount > 15:
                time.sleep(180)
            elif reconnectCount > 10:
                time.sleep(120)
            elif reconnectCount > 5:
                time.sleep(60)
            else:
                time.sleep(10)
        else:
            time.sleep(10)

# 测试以太网是否可用
def ethDeviceCheck():
    global ppp0used,timeThread,ethUsed,ethcanUsed,reconnectCount,netMonitorStart
    defRoute = getDefRoutes()
    initRouteTable()
    rst = os.popen("ping 119.29.29.29 -i0.1 -w1 -c4").read().split()
    if '100%' in rst:               # 网线不通的情况下
        ethcanUsed = False
        if not ppp0used:    # 尝试进行ppp0拨号 启动拨号线程。
            threading.Thread(target=connect4G).start()
            ppp0used = True
        if DEBUG: log('The eth0 device is unavailable')
        if hasppp0():               # 如果存在4G的情况下
            # 如果默认路由不是 (只有一条而且这条路由还是ppp0 ) 就切换到4G
            reconnectCount = 0
            if not (len(defRoute) == 1 and 'ppp0' in defRoute[0].split()):
                switchTo4G()
                log('Switch to ppp0...')
            if not timeThread:
                threading.Thread(target=timeSync).start()
                timeThread = True
            if not netMonitorStart:
                netMonitor().start()  # 在启用4G的时候启用网络监控线程
                netMonitorStart = True
    else:                           # 网线通的情况下
        if DEBUG: log('The eth0 device is available, PING: 119.29.29.29 AVG: '+rst[-2].split('/')[1]+ ' ms')
        ethcanUsed = True
        # 如果默认路由不是 (只有一条而且这条路由还是eth0) 就切换到网线
        if not (len(defRoute) == 1 and 'eth0' in defRoute[0].split()):
            switchToEth()
            log('Switch to eth0...')
        if not timeThread:
            threading.Thread(target=timeSync).start()
            timeThread = True

if __name__ == '__main__':
    time.sleep(10)
    while True:
        ethDeviceCheck()
        time.sleep(10)