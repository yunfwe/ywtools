#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-19

from __future__ import (print_function, unicode_literals)

__author__ = 'weiyunfei'
__date__ = '2017-09-19'
__version__ = '0.1'

import os
import sys
__python__ = sys.version_info[0]
import time
import getopt
if __python__ == 3:
    import configparser
elif __python__ == 2:
    configparser = __import__('ConfigParser')


class Errors(object):
    pass

class Utils(object):
    @staticmethod
    def datetime():
        """
        :return: time.strftime('%Y-%m-%d %H:%M:%S')
        """
        return time.strftime('%Y-%m-%d %H:%M:%S')
    @staticmethod
    def timeit(enable=True):
        """
        Same as timeit.timeit()
        Get used time of function execution.
        
        Decorator:
        @Utils.timeit(enable=True)
        def func():
            pass
        
        :param enable: True or False [default=True]
        :return: 
            if enable is True 
            return: tuple(result, used_time)
            
            if enable is False
            return: result
            
            else
            raise ValueError
        """
        if enable not in (True, False):
            raise ValueError('enable: Only True or False')
        def _timeit(func):
            def _func(*args, **kwargs):
                now = time.time()
                rst = func(*args, **kwargs)
                if enable is True:
                    time.sleep(0.0001)
                    return rst, time.time() - now
                elif enable is False:
                    return rst
            return _func
        return _timeit

    @staticmethod
    def logConfig(logFile=None):
        import logging
        if logFile is None:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s [remotescript] %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',)
            return logging
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s [remotescript] %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=logFile,
                                filemode='w')
            return logging

    @staticmethod
    def random(size=16):
        pool = list(range(97, 123)) + list(range(65, 91)) + list(range(48, 58))
        _str = ''
        for i in range(size):
            _str += chr(__import__('random').choice(pool))
        return _str


class Config(object):
    """
    优先级：命令行参数 > hosts文件 > 环境变量 > 配置文件 > 程序内置
    """
    config = {
        # 'ssh_host': '127.0.0.1',
        'ssh_hosts': [],
        # 'ssh_group': None,
        'ssh_groups': [],
        'ssh_port': 22,
        'ssh_username': 'root',
        'ssh_password': None,
        'scripts_dir': '/usr/share/remotescripts/',
        'config_file': '/etc/remotescript.conf',
        'ssh_connect_timeout': 5,
        'ssh_execute_timeout': 60,
        'log_file': '/var/log/remotescript.log',
        'script': None,
        'debug': False,
        'inventory_file': './hosts'
    }

    @staticmethod
    def parseEnvironVar():
        pass

    @staticmethod
    def parseConfigFile():
        if not os.path.exists(Config.config['config_file']):return
        _config = {}
        cf = configparser.ConfigParser()
        cf.read(Config.config['config_file'])
        for s in cf.sections():
            _config[s] = dict(cf.items(s))

        # parse general section
        for opt,val in _config.get('general',{}):
            if opt == 'default_scripts_dir':
                Config.config['scripts_dir'] = val;continue
            if opt == 'log_file':
                Config.config['log_file'] = val;continue

        # parse ssh section
        for opt,val in _config.get('ssh',{}):
            if opt == 'default_ssh_host':
                Config.config['ssh_host'] = val;continue
            if opt == 'default_ssh_port':
                Config.config['ssh_port'] = int(val);continue
            if opt == 'default_ssh_username':
                Config.config['ssh_username'] = val;continue
            if opt == 'default_ssh_password':
                Config.config['ssh_password'] = val;continue
            if opt == 'default_ssh_connect_timeout':
                Config.config['ssh_connect_timeout'] = int(val);continue
            if opt == 'default_ssh_auth_timeout':
                Config.config['ssh_auth_timeout'] = int(val);continue
            if opt == 'default_ssh_execute_timeout':
                Config.config['ssh_execute_timeout'] = int(val);continue

    @staticmethod
    def parseHostsFile():
        if not os.path.exists(Config.config['hosts_file']):return

    @staticmethod
    def parseEnvironVar():
        """
        REMOTE_SSH_HOSTS : ssh_hosts
        REMOTE_SSH_USERNAME : ssh_username
        REMOTE_SSH_PASSWORD : ssh_password
        REMOTE_CONFIG_FILE : config_file
        REMOTE_LOG_FILE : log_file
        REMOTE_SCRIPTS_DIR : scripts_dir
        :return: 
        """
        if os.environ.get('REMOTE_SSH_HOSTS'):
            Config.config['ssh_hosts'] = os.environ.get('REMOTE_SSH_HOSTS').split(',')
        if os.environ.get('REMOTE_SSH_USERNAME'):
            Config.config['ssh_username'] = os.environ.get('REMOTE_SSH_USERNAME')
        if os.environ.get('REMOTE_SSH_PASSWORD'):
            Config.config['ssh_password'] = os.environ.get('REMOTE_SSH_PASSWORD')
        if os.environ.get('REMOTE_CONFIG_FILE'):
            Config.config['config_file'] = os.environ.get('REMOTE_CONFIG_FILE')
        if os.environ.get('REMOTE_LOG_FILE'):
            Config.config['log_file'] = os.environ.get('REMOTE_LOG_FILE')
        if os.environ.get('REMOTE_SCRIPTS_DIR'):
            Config.config['scripts_dir'] = os.environ.get('REMOTE_SCRIPTS_DIR')


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
                '# default_ssh_connect_timeout = 10\n'
                '# default_ssh_execute_timeout = 60\n\n')
    if not os.path.exists(Config.config['scripts_dir']):
        try:
            print('Create directory %s ...' % Config.config['scripts_dir'])
            os.mkdir(Config.config['scripts_dir'])
        except Exception as e:
            sys.stderr.write("Create %s failed!\nReason: %s\n" % (Config.config['scripts_dir'],str(e)))
            sys.exit(1)
    else:
        print('Directory: %s already existed! Nothing to do.' % Config.config['scripts_dir'])

    if not os.path.exists(Config.config['config_file']):
        try:
            print('Write config template into %s ...' % Config.config['config_file'])
            open(Config.config['config_file'],'w').write(template)
        except Exception as e:
            sys.stderr.write("mkdir: /usr/share/remotescripts/ failed!\nReason: %s\n" % str(e))
            sys.exit(1)
    else:
        print('Used config file: %s' % Config.config['config_file'])
    print('All initialization successful!')

class SSH(object):
    def __init__(self,hostname=None,port=22,username=None,password=None,timeout=5):
        try:
            paramiko = __import__('paramiko')
        except ImportError:
            sys.stderr.write('Error! Module: paramiko is not found!')
            sys.stderr.flush()
            sys.exit(2)
        self._ssh = paramiko.SSHClient()
        self.info = (hostname, port, username)
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._ssh.connect(hostname=hostname, port=port, username=username,
                              password=password, timeout=timeout)
        except Exception as e:
            sys.stderr.write('Error! Host {ip}: connect '.format(ip=hostname) + str(e) + '\n')
            sys.stderr.flush()
            sys.exit(2)
        self.sftp = self._ssh.open_sftp()
    def _execute(self, command, timeout=None):
        return self._ssh.exec_command("bash -c \"{cmd}\"".format(cmd=command), get_pty=True,
                                      timeout=timeout)
    def execute(self, command, timeout=None):
        rst_stdin, rst_stdout, rst_stderr =  self._ssh.exec_command("bash -c \"{cmd}\"".format(cmd=command), get_pty=True,
                                      timeout=timeout)
        return ''.join(rst_stdout.readlines()), ''.join(rst_stderr.readlines()), rst_stdout.channel.recv_exit_status()
    def putfile(self, src=None, dest=None, mode=None):
        if mode is None:
            mode = os.stat(src)[0]
        self.sftp.put(src, dest)
        self.sftp.chmod(dest,mode=mode)
    def getfile(self, src, dest, mode=None):
        if mode is None:
            mode = self.sftp.stat(src).st_mode
        self.sftp.get(src, dest)
        os.chmod(dest,mode)
    def close(self):self._ssh.close()




class ParseOptions(object):
    options = sys.argv[2:]

    def __init__(self):
        try:
            options,args = getopt.getopt(ParseOptions.options,'vhH:U:P:p:t:s:c:a:',['help','host=','port=','username=',
                                         'password=','script=','init','version','--sudo', '--sudo-pass'
                                        'connect-timeout=','append=','execute-timeout=','scripts-dir=','config='])
        except getopt.GetoptError as e:
            print(str(e)+'\n'+ParseOptions.usage())
            sys.exit(255)

    @staticmethod
    def usage():
        __doc__ = ('remotescript Version: {ver}\n'
                   'Get the results of the remote host execution script.\n'
                   '    \n'
                   'Usage: remotescript <action> -H <host> -U <username> -P <password> -s <script>\n'
                   '\n'
                   '  Actions:\n'
                   '    cmd                             Run command from remote host.\n'
                   '    get                             Get file from remote host.\n'
                   '    put                             Put file to remote host.\n'
                   '    script                          Run command from remote host.\n'
                   '\n'
                   '  Options:\n'
                   '    -h, --help                      Display this help and exit.\n'
                   '    -v, --version                   Display version information.\n'
                   '    -H, --host=<host>               Connect to host. [default=127.0.0.1]\n'
                   '    -G, --group=<host>              Connect all hosts with in a group.\n'
                   '    -i, --inventory=<filename>      Host inventory file, host or group can define in it. [default="./hosts"]\n'
                   '    -U, --username=<username>       username to use when connecting to server. [default=root]\n'
                   '    -P, --password=<password>       Password to use when connecting to server.\n'
                   '    -f, --fork=<host>               Connect to host. [default=127.0.0.1]\n'
                   '    -T, --threads=<host>            Connect to host. [default=127.0.0.1]\n'
                   '    -p, --port=<port>               Port number to use for connecting to server. [default=22]\n'
                   '    -t, --execute-timeout=<number>  Timeout for script execution. [default=60]\n'
                   '    -s, --script=<script-name>      Execution this script in remote host. [vaild in script action]\n'
                   '    -a, --append=<arguments>        Pass arguments to the script.\n'
                   '    -c, --config=<path>             Use this config file. [default=/etc/remotescript.conf]\n'
                   '    \n'
                   '    --sep                           If use --append option, Use sep for arguments. [default=" "]\n'
                   '    --init                          Initialization config file and running environment.\n'
                   '    --sudo                          Run operations with sudo. [vaild in cmd and script action]\n'
                   '    --sudo-pass                     If have --sudo option, ask for sudo password. [vaild in cmd and script action]\n'
                   '    --scripts-dir=<abspath>         If the script name is only the filename, it will be search in this directory. [default=/usr/share/remotescripts/]\n'
                   '    --connect-timeout=<number>      Timeout for host connect. [default=10]\n'.format(ver=__version__))
        return __doc__


def main():
    pass


if __name__ == '__main__':
    main()
