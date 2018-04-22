#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-04-20

import os
import sys
import IPy
import time
import fcntl
import struct
import socket
import select
import hashlib
import threading
import collections

BUFFER_SIZE = 8192
BIND_ADDRESS = '0.0.0.0',2001
NETWORK = '172.16.10.0/24'
MTU = 1400
KEEPALIVE = 10

ipRange = list(map(lambda x:x.__str__(), IPy.IP(NETWORK)))[1:-1]
localIp = ipRange.pop(0)

class Machine(object):
    @staticmethod
    def getMacAddress(interface='eth0'):
        try:
            with open('/sys/class/net/%s/address' % interface) as f:
                return f.read().strip()
        except IOError:
            class InterfaceNotFound(Exception):pass
            raise InterfaceNotFound('[Error] No such interface')
    @staticmethod
    def getStaticMachineCode():
        code = Machine.getMacAddress()+'9fc3d2c5'
        return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]
    @staticmethod
    def getDynamicMachineCode():
        salt = str(int(str(time.time())[:8]) ^ 10220000)
        code = Machine.getStaticMachineCode() + salt
        return hashlib.md5(code.encode('utf-8')).hexdigest()[:8]

class NetTools(object):
    @staticmethod
    def ip2int(ip):
        return struct.unpack('!I', socket.inet_aton(ip))[0]

    @staticmethod
    def createTunnel(tunName='tun'):
        try:
            tunfd = os.open("/dev/net/tun", os.O_RDWR)
        except FileNotFoundError:
            raise Exception('Your device not support tunnel.')
        if tunfd < 0:
            raise Exception('Failed to create tun device.')
        if not type(tunName) is bytes: tunName = tunName.encode()
        fcntl.ioctl(tunfd, 0x400454ca, struct.pack(b"16sH", tunName, 0x0001 | 0x1000))
        return tunfd

    @staticmethod
    def startTunnel(tunName, lip, pip, mtu=MTU):
        os.popen('ifconfig %s %s dstaddr %s mtu %s up' % (tunName, lip, pip, mtu)).read()

    @staticmethod
    def addRoute(nw, gw):
        os.popen('ip ro add %s via %s' % (nw, gw)).read()


class Server(object):
    sessions = []
    readables = []
    ss = collections.namedtuple('ss',['tunName', 'tunfd', 'addr', 'peerIp', 'time'])

    def __init__(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(BIND_ADDRESS)
        self.udp.settimeout(10)
        Server.readables.append(self.udp)
        print('Server is listen on %s:%s...' % BIND_ADDRESS)

    @staticmethod
    def getTunByAddr(addr):
        for i in Server.sessions:
            if i.addr == addr: return i.tunfd

    @staticmethod
    def getAddrByTun(tunfd):
        for i in Server.sessions:
            if i.tunfd == tunfd: return i.addr

    @staticmethod
    def Auth(data):
        """

        :param data:
        :return: True or False

        客户端发送自己的机器码和动态码到服务端
        服务端根据算法计算客户端的机器码和动态码是否匹配
        如果匹配 返回True，否则返回False
        """
        try:
            data = data.decode()
        except UnicodeDecodeError:
            return 'Timeout'

        if data == 'live':
            return 'Timeout'

        if not data.startswith('Hi?'): return False
        try:
            code = data[3:].split(';')
            for i in Server.sessions:
                if i.tunName == code[0]:
                    Server.sessions.remove(i)
                    Server.readables.remove(i.tunfd)
                    os.close(i.tunfd)
                    ipRange.insert(0,i.peerIp)
            salt = str(int(str(time.time())[:8]) ^ 10220000)
            val = code[0] + salt
            return code[1] == hashlib.md5(val.encode('utf-8')).hexdigest()[:8]
        except IndexError: return False

    def run_forever(self):
        print('Start processing client requests...')
        while True:
            # print(Server.sessions)
            readable = select.select(Server.readables, [], [], 2)[0]
            for r in readable:
                if r == self.udp:
                    data, addr = self.udp.recvfrom(BUFFER_SIZE)
                    try:
                        tunfd = Server.getTunByAddr(addr)
                        if not tunfd:
                            rst = Server.Auth(data)
                            if not rst:continue
                            if rst == 'Timeout':
                                self.udp.sendto(b'reconnect', addr)
                                continue
                            tunName = data.decode()[3:].split(';')[0]
                            tunfd = NetTools.createTunnel(tunName)
                            peerIp = ipRange.pop(0)
                            NetTools.startTunnel(tunName,localIp,peerIp)
                            info = Server.ss(tunName=tunName,tunfd=tunfd,addr=addr,peerIp=peerIp,time=time.time())
                            Server.sessions.append(info)
                            Server.readables.append(tunfd)
                            reply = ';'.join([info.tunName,info.peerIp,localIp,NETWORK]).encode()
                            self.udp.sendto(reply, addr)
                            print('Clinet %s:%s connect successful' % addr)
                        else:
                            os.write(tunfd,data)
                    except OSError:continue
                else:
                    try:
                        addr = Server.getAddrByTun(r)
                        data = os.read(r, BUFFER_SIZE)
                        self.udp.sendto(data,addr)
                    except Exception:
                        pass

class Client(object):
    def __init__(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.to = '47.104.178.134',2001
        self.udp.settimeout(10)
        self.tunfd = None
        self.machineCode = None

    def keepalive(self):
        """
        因为NAT模型的原因，客户端需要保持跟服务端在路由器上的session
        """
        def _keepalive(udp, to):
            while True:
                time.sleep(KEEPALIVE)
                udp.sendto(b'live', to)
        threading.Thread(target=_keepalive, args=(self.udp, self.to), name='keepalive').start()


    def login(self):
        self.machineCode = Machine.getStaticMachineCode()
        data = 'Hi?'+';'.join([self.machineCode, Machine.getDynamicMachineCode()])
        self.udp.sendto(data.encode(),self.to)
        try:
            reply, addr = self.udp.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            return
        info = reply.decode().split(';')
        try:
            self.tunfd = NetTools.createTunnel(info[0])
            NetTools.startTunnel(info[0],info[1],info[2],info[3])
            NetTools.addRoute(info[3], info[2])
            return True
        except IndexError:
            return

    def run_forever(self):
        print('Start connect to server...')
        if self.login() is None:
            print('Connect failed!')
            sys.exit(0)
        print('Connect to server successful')
        self.keepalive()
        while True:
            readable = select.select([self.udp, self.tunfd], [], [], 1)[0]
            for r in readable:
                if r == self.udp:
                    data, addr = self.udp.recvfrom(BUFFER_SIZE)
                    try:
                        os.write(self.tunfd, data)
                    except OSError:
                        if data.decode() == 'reconnect':
                            os.close(self.tunfd)
                            if self.login() is None:
                                print('Reconnect failed!')
                else:
                    data = os.read(self.tunfd, BUFFER_SIZE)
                    self.udp.sendto(data, self.to)


Server().run_forever()
Client().run_forever()