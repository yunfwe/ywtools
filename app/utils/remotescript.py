#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-17

from __future__ import (print_function,unicode_literals)

# global config

# 实现基础的命令执行 文件拷贝 脚本执行
# 后期实现并发控制 计时功能 日志记录 set/get 修改和获取配置文件内容
# 提供接口API供其它脚本调用
# 支持多个主机 支持普通用户sudo  支持远程脚本传参

__author__ = 'weiyunfei'
__date__ = '2017-09-17'
__version__ = '0.0.1'


import os
import sys
__python__ = sys.version_info[0]
import getopt
import paramiko
if __python__ == 3:
    import configparser
elif __python__ == 2:
    configparser = __import__('ConfigParser')
import random as rdm
from socket import timeout
from getpass import getpass


curconfig = {
    'ssh_host': '127.0.0.1',
    'ssh_port': 22,
    'ssh_username': 'root',
    'ssh_password': None,
    'scripts_dir': '/usr/share/remotescripts/',
    'config_file': '/etc/remotescript.conf',
    'connect_timeout': 10,
    'auth_timeout': 10,
    'exec_timeout': 60,
    'log_file': '/var/log/remotescript.log',
    'script': None,
}

def configParse():
    # if not os.path.exists(curconfig['config_file']):
    #     print('Error: config file is not exists! ["%s"]' % curconfig['config_file'])
    #     print('Please run "remotescript --init" first.')
    #     sys.exit(1)
    if not os.path.exists(curconfig['config_file']):return
    config = []
    cf = configparser.ConfigParser()
    cf.read(curconfig['config_file'])
    for s in cf.sections():
        config += cf.items(s)
    for opt,val in config:
        if opt == 'default_ssh_host':
            curconfig['ssh_host'] = val;continue
        if opt == 'default_ssh_port':
            curconfig['ssh_port'] = int(val);continue
        if opt == 'default_ssh_username':
            curconfig['ssh_username'] = val;continue
        if opt == 'default_ssh_password':
            curconfig['ssh_password'] = val;continue
        if opt == 'default_connect_timeout':
            curconfig['connect_timeout'] = int(val);continue
        if opt == 'default_auth_timeout':
            curconfig['auth_timeout'] = int(val);continue
        if opt == 'default_exec_timeout':
            curconfig['exec_timeout'] = int(val);continue
        if opt == 'default_scripts_dir':
            curconfig['scripts_dir'] = val;continue
        if opt == 'log_file':
            curconfig['log_file'] = val
        # curconfig[opt] = val


# 初始化配置文件和运行环境
def init():
    template = ('[general]\n'
                '# default_scripts_dir = /usr/share/remotescripts/\n'
                '# log_file = /var/log/remotescript.log\n'
                '\n'
                '[ssh]\n'
                '# default_ssh_host = 127.0.0.1\n'
                '# default_ssh_port = 22\n'
                '# default_ssh_username = root\n'
                '# default_ssh_password = 111111\n'
                '\n'
                '[timeout]\n'
                '# default_connect_timeout = 10\n'
                '# default_auth_timeout = 10\n'
                '# default_exec_timeout = 60\n')
    if not os.path.exists(curconfig['scripts_dir']):
        try:
            print('Create directory %s ...' % curconfig['scripts_dir'])
            os.mkdir(curconfig['scripts_dir'])
        except Exception as e:
            sys.stderr.write("Create %s failed!\nReason: %s\n" % (curconfig['scripts_dir'],str(e)))
            sys.exit(1)
    else:
        print('Directory: %s already existed! Nothing to do.' % curconfig['scripts_dir'])

    if not os.path.exists(curconfig['config_file']):
        try:
            print('Write config template into %s ...' % curconfig['config_file'])
            open(curconfig['config_file'],'w').write(template)
        except Exception as e:
            sys.stderr.write("mkdir: /usr/share/remotescripts/ failed!\nReason: %s\n" % str(e))
            sys.exit(1)
    else:
        print('Used config file: %s' % curconfig['config_file'])
    print('All initialization successful!')


def random(size=16):
    pool = list(range(97, 123)) + list(range(65, 91)) + list(range(48, 58))
    _str = ''
    for i in range(size):
        _str += chr(rdm.choice(pool))
    return _str

def stderr(host,e):
    sys.stderr.write('Error! Host {ip}: '.format(ip=host) + str(e) + '\n')
    sys.stderr.flush()

def sshConnect(hostname=None,port=22,username=None,password=None,timeout=None,auth_timeout=None):
    _ssh = paramiko.SSHClient()
    _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        _ssh.connect(hostname=hostname, port=port,
                     username=username, password=password,
                     timeout=timeout, auth_timeout=auth_timeout)
    except Exception as e:
        sys.stderr.write('Error! Host {ip}: connect or auth '.format(ip=hostname) + str(e) + '\n')
        sys.stderr.flush()
        sys.exit(2)
    return _ssh, (hostname, port, username)


def scp(ssh=None, src=None):
    try:
        sftp = ssh[0].open_sftp()
    except Exception as e:
        stderr(ssh[1][0],e)
        sys.exit(2)
    if ssh[1][2] == 'root':
        homePath = '/root'
    else:
        homePath = os.path.join('/home', ssh[1][2])
    if src[-1] == '/':
        sys.stderr.write("You should privode file path instead of directory path.\n")
        sys.stderr.flush()
        sys.exit(2)
    if '/' in src:
        srcPath = src
        dstfile = os.path.split(srcPath)[-1]
    else:
        if os.path.exists('./%s' % src):
            srcPath = './'+src
            dstfile = os.path.split(srcPath)[-1]
        else:
            srcPath = os.path.join(curconfig['scripts_dir'], src)
            dstfile = src
    destPath = os.path.join(homePath, '.remotescripts/', dstfile+random())
    try:
        sftp.stat(os.path.dirname(destPath))
    except FileNotFoundError:
        try:
            sftp.mkdir(os.path.dirname(destPath))
        except PermissionError as e:
            stderr(ssh[1][0],e)
            sys.exit(2)
    try:
        sftp.put(srcPath, destPath)
        sftp.chmod(destPath,mode=493)
    except Exception as e:
        stderr(ssh[1][0],e)
        sys.exit(2)
    return destPath

def execute(ssh=None,cmdPath=None):
    rst_stdin, rst_stdout, rst_stderr = ssh[0].exec_command("bash -c \"{cmd}\"".format(cmd=cmdPath),
                                                            get_pty=True,
                                                            timeout=int(curconfig['exec_timeout']))
    del rst_stdin
    try:
        result = ''.join(rst_stdout.readlines())
    except timeout as e:
        del e
        stderr(ssh[1][0],'timeout!')
        sys.exit(2)
    err = ''.join(rst_stderr.readlines())
    if err:
        sys.stderr.write(err)
    if result:
        sys.stdout.write(result)
    ssh[0].exec_command("bash -c \"rm -rf {cmd}\"".format(cmd=cmdPath),get_pty=True)
    sys.exit(rst_stdout.channel.recv_exit_status())


def usage():
    __doc__ = '''remotescript Version: {ver}
Gets the results of the remote host execution script.
    
Usage: remotescript -H <host> -U <username> -P <password> -s <script>

  Options:
    -h, --help                      Display this help and exit.
    -v, --version                   Display version information.
    -H, --host=<host>               Connect to host. [default=127.0.0.1]
    -U, --username=<username>       username to use when connecting to server. [default=root]
    -P, --password=<password>       Password to use when connecting to server.
    -p, --port=<port>               Port number to use for connecting to server. [default=22]
    -t, --exec-timeout=<number>     Timeout for script execution. [default=60]
    -s, --script=<script-name>      Execution this script in remote host. 
    -c, --config=<path>             Use this config file. [default=/etc/remotescript.conf]
    
    --init                          Initialization config file and running environment.
    --scripts-dir=<abspath>         If the script-name is only the filename, it will be found in this directory. [default=/usr/share/remotescripts/]
    --connect-timeout=<number>      Timeout for host connect. [default=10]
    --auth-timeout=<number>         Timeout for user authentication. [default=10]
'''.format(ver=__version__)
    return __doc__

def main():
    try:
        options,args = getopt.getopt(sys.argv[1:],'vhH:U:P:p:t:s:c:',
                  ['help','host=','port=','username=','password=','script=','init','version',
                   'connect-timeout=','auth-timeout=','exec-timeout=','scripts-dir','config'])
    except getopt.GetoptError as e:
        print(str(e)+'\n'+usage())
        sys.exit(255)
    # if not options:print(usage());sys.exit(1)
    configParse()
    for name,value in options:
        if name == '--init':
            init()
            sys.exit(0)
        if name in ('-h','--help'):
            print(usage())
            sys.exit(0)
        if name in ('-v','--version'):
            print(__version__)
            sys.exit(0)
        if name in ('-c','--config'):
            curconfig['config_file'] = value
            configParse()
        if name in ('-H','--host'):
            curconfig['ssh_host'] = value
        if name in ('-U','--user'):
            curconfig['ssh_username'] = value
        if name in ('-P','--password'):
            curconfig['ssh_password'] = value
        if name in ('-p','--port'):
            curconfig['ssh_port'] = int(value)
        if name in ('-t','--exec-timeout'):
            curconfig['exec_timeout'] = int(value)
        if name in ('-s','--script'):
            curconfig['script'] = value
        if name == '--scripts-dir':
            curconfig['scripts_dir'] = value
        if name == '--connect-timeout':
            curconfig['connect_timeout'] = int(value)
        if name == '--auth-timeout':
            curconfig['auth_timeout'] = int(value)
    if not curconfig['script']:
        sys.stderr.write("You must privode file path of script!\n")
        sys.stderr.flush()
        sys.exit(1)
    # print(curconfig)
    if not curconfig['ssh_password']:
        print('Not found paasword from argv or config file, but you must provide it.')
        curconfig['ssh_password'] = getpass("Please input password: ")
    ssh = sshConnect(hostname=curconfig['ssh_host'], port=curconfig['ssh_port'],
                     username=curconfig['ssh_username'], password=curconfig['ssh_password'],
                     timeout=curconfig['connect_timeout'], auth_timeout=curconfig['auth_timeout'])
    dest = scp(ssh=ssh,src=curconfig['script'])
    execute(ssh=ssh,cmdPath=dest)
    print(curconfig)

if __name__ == '__main__':
    main()