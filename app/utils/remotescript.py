#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-19

from __future__ import (print_function, unicode_literals)

__author__ = 'weiyunfei'
__date__ = '2017-09-19'
__version__ = '0.0.2'

import os
import sys

__python__ = sys.version_info[0]
import time
import getopt
import configparser
from socket import timeout


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
                                datefmt='%Y-%m-%d %H:%M:%S', )
            return logging
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s [remotescript] %(levelname)s: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                filename=logFile,
                                filemode='a')
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
    优先级：命令行参数 > 环境变量 > 配置文件 > 程序内置
    """
    config = {
        'ssh_host': '127.0.0.1',
        'ssh_groups': [],
        'ssh_port': 22,
        'ssh_username': 'root',
        'ssh_password': None,
        'ssh_su_password': None,
        'scripts_dir': '/usr/share/remotescripts/',
        'config_file': '/etc/remotescript.conf',
        'ssh_connect_timeout': 10,
        'ssh_auth_timeout': 10,
        'ssh_execute_timeout': 60,
        'log_file': '/tmp/remotescript.log',
        'script': None,
        'append': None,
        'debug': False,
        'sep': None
    }

    @staticmethod
    def parseEnvironVar():
        pass

    @staticmethod
    def parseConfigFile():
        if not os.path.exists(Config.config['config_file']): return
        _config = {}
        cf = configparser.ConfigParser()
        cf.read(Config.config['config_file'])
        for s in cf.sections():
            _config[s] = dict(cf.items(s))

        # parse general section
        for opt, val in _config.get('general', {}).items():
            if opt == 'default_scripts_dir':
                Config.config['scripts_dir'] = val
                continue
            if opt == 'log_file':
                Config.config['log_file'] = val
                continue

        # parse ssh section
        # print(_config.get('ssh',{}));exit(1)
        for opt, val in _config.get('ssh', {}).items():
            if opt == 'default_ssh_host':
                Config.config['ssh_host'] = val
                continue
            if opt == 'default_ssh_port':
                Config.config['ssh_port'] = int(val)
                continue
            if opt == 'default_ssh_username':
                Config.config['ssh_username'] = val
                continue
            if opt == 'default_ssh_password':
                Config.config['ssh_password'] = val
                continue
            if opt == 'default_ssh_connect_timeout':
                Config.config['ssh_connect_timeout'] = int(val)
                continue
            if opt == 'default_ssh_auth_timeout':
                Config.config['ssh_auth_timeout'] = int(val)
                continue
            if opt == 'default_ssh_execute_timeout':
                Config.config['ssh_execute_timeout'] = int(val)
                continue

    @staticmethod
    def parseHostsFile():
        if not os.path.exists(Config.config['hosts_file']): return

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
                '# log_file = /tmp/remotescript.log\n'
                '\n'
                '[ssh]\n'
                '# default_ssh_host = 127.0.0.1\n'
                '# default_ssh_port = 22\n'
                '# default_ssh_username = root\n'
                '# default_ssh_password = 111111\n'
                '# default_ssh_connect_timeout = 10\n'
                '# default_ssh_auth_timeout = 10\n'
                '# default_ssh_execute_timeout = 60\n\n')
    if not os.path.exists(Config.config['scripts_dir']):
        try:
            print('Create directory %s ...' % Config.config['scripts_dir'])
            os.mkdir(Config.config['scripts_dir'])
        except Exception as e:
            sys.stderr.write("Create %s failed!\nReason: %s\n" % (Config.config['scripts_dir'], str(e)))
            sys.exit(1)
    else:
        print('Directory: %s already existed! Nothing to do.' % Config.config['scripts_dir'])

    if not os.path.exists(Config.config['config_file']):
        try:
            print('Write config template into %s ...' % Config.config['config_file'])
            open(Config.config['config_file'], 'w').write(template)
        except Exception as e:
            sys.stderr.write("mkdir: /usr/share/remotescripts/ failed!\nReason: %s\n" % str(e))
            sys.exit(1)
    else:
        print('Used config file: %s' % Config.config['config_file'])
    print('All initialization successful!')


class SSH(object):
    def __init__(self, hostname=None, port=22, username=None, password=None, timeout=5, auth_timeout=5):
        try:
            import paramiko
        except ImportError:
            sys.stderr.write('Error! Module: paramiko is not found!\n')
            sys.stderr.flush()
            sys.exit(2)
        self._ssh = paramiko.SSHClient()
        self.info = (hostname, port, username)
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._ssh.connect(hostname=hostname, port=port, username=username,
                              password=password, timeout=timeout, auth_timeout=auth_timeout)
        except Exception as e:
            sys.stderr.write('Error! Host {ip}: '.format(ip=hostname) + str(e) + '\n')
            log.error('Host {ip}: '.format(ip=hostname) + str(e))
            sys.stderr.flush()
            sys.exit(2)
        self.sftp = self._ssh.open_sftp()
    def _execute(self, command, timeout=None):
        return self._ssh.exec_command(command, get_pty=True, timeout=timeout)
        # return self._ssh.exec_command("bash -c \"{cmd}\"".format(cmd=command), get_pty=True, timeout=timeout)
    def execute(self, command, timeout=None):
        rst_stdin, rst_stdout, rst_stderr = self._ssh.exec_command(command, get_pty=True,timeout=timeout)
        try:
            return ''.join(rst_stdout.readlines()), ''.join(
                rst_stderr.readlines()), rst_stdout.channel.recv_exit_status()
        except timeout:
            sys.stdout.write('Warnning: Host {ip}: execute "{cmd}" timeout!\n'.format(ip=self.info[0], cmd=command))
            log.warning('Host {ip}: execute "{cmd}" timeout!\n'.format(ip=self.info[0], cmd=command))
            sys.exit(2)
    def putfile(self, src=None, dest=None, mode=None):
        if mode is None:
            mode = os.stat(src)[0]
        self.sftp.put(src, dest)
        self.sftp.chmod(dest, mode=mode)
    def getfile(self, src, dest, mode=None):
        if mode is None:
            mode = self.sftp.stat(src).st_mode
        self.sftp.get(src, dest)
        os.chmod(dest, mode)
    def close(self):
        self._ssh.close()


def cmd(ssh, cf):
    if cf['append'] is None:
        sys.stderr.write('You must privode -a or --append for cmd action! Use --help see more.\n')
        sys.exit(1)
    if not cf['sep'] is None:
        cf['append'] = ' '.join(cf['append'].split(cf['sep']))

    if cf.get('su'):
        if not cf['ssh_su_password']:
            cf['ssh_su_password'] = __import__('getpass').getpass("Remote %s's password: " % cf['su'])
        rst = ssh._execute('su - {user} -c "'.format(user=cf['su']) + cf['append'] + '"',
                           timeout=cf['ssh_execute_timeout'])
        try:
            if rst[1].read(1):
                rst[0].write(cf['ssh_su_password'] + '\n')
            err = ''.join(rst[2].readlines()[1:])
            if err:
                print(err)
                sys.stderr.write(err)
                sys.stderr.flush()
            result = ''.join(rst[1].readlines()[1:])
            if result:
                sys.stdout.write(result)
        except timeout:
            sys.stdout.write('Warnning: Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            log.warning('Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            sys.exit(2)
        log.info('Host {ip}: execute "{cmd}" successful!'.format(ip=ssh.info[0], cmd=cf['append']))
        return rst[1].channel.recv_exit_status()
    elif cf.get('sudo'):
        if cf['append'][:5] == 'sudo ':
            rst = ssh._execute(cf['append'], timeout=cf['ssh_execute_timeout'])
        else:
            rst = ssh._execute('sudo -i ' + cf['append'], timeout=cf['ssh_execute_timeout'])
        try:
            if rst[1].read(1):
                rst[0].write(cf['ssh_password'] + '\n')
            err = ''.join(rst[2].readlines()[1:])
            if err:
                sys.stderr.write(err)
            result = ''.join(rst[1].readlines()[1:])
            if result:
                sys.stdout.write(result)
        except timeout:
            sys.stdout.write('Warnning: Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            log.warning('Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            sys.exit(2)
        log.info('Host {ip}: execute "{cmd}" successful!'.format(ip=ssh.info[0], cmd=cf['append']))
        return rst[1].channel.recv_exit_status()
    else:
        try:
            rst = ssh.execute(cf['append'], timeout=cf['ssh_execute_timeout'])
        except:
            sys.stdout.write('Warnning: Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            log.warning('Host {ip}: execute "{cmd}" timeout!\n'.format(ip=ssh.info[0], cmd=cf['append']))
            sys.exit(2)
        if rst[1]: sys.stderr.write(rst[1])
        if rst[0]: sys.stdout.write(rst[0])
        log.info('Host {ip}: execute "{cmd}" successful!'.format(ip=ssh.info[0], cmd=cf['append']))
        return rst[2]


def put(ssh, cf):
    try:
        src = cf['src']
        dest = cf['dest']
    except KeyError:
        print('You must privode --src and --dest for put or get action! Use --help see more.')
        sys.exit(1)
    if not os.path.exists(src):
        sys.stdout.write('Error: No such file or directory: \'%s\'\n' % src)
        sys.exit(1)
    if not os.path.isfile(src):
        sys.stdout.write('Error: Don\'t support directory!\n')
        sys.exit(1)
    if dest[-1] == '/':
        dest = os.path.join(dest, os.path.split(src)[-1])
    try:
        ssh.sftp.stat(dest)
    except FileNotFoundError:
        pass
    else:
        print('Error: Remote file already exists! \'%s\'' % dest)
        sys.exit(1)
    try:
        ssh.putfile(src=src, dest=dest)
    except PermissionError as e:
        sys.stdout.write('Error: %s!' % str(e))
        sys.exit(1)
    except FileNotFoundError:
        sys.stdout.write('Error: The destination path does not exist! %s\n' % dest)
        sys.exit(1)
    except Exception as e:
        sys.stdout.write('Error: %s\n' % str(e))
        sys.exit(1)
    log.info("Host: %s [Put]  src: %s  dest: %s successful" % (ssh.info[0], src, dest))
    return src, dest


def get(ssh, cf):
    try:
        src = cf['src']
        dest = cf['dest']
    except KeyError:
        print('You must privode --src and --dest for put or get action! Use --help see more.')
        sys.exit(1)

    if dest[-1] == '/':
        if not os.path.exists(dest):
            print('Error: Directory not exists! \'%s\'' % dest)
            sys.exit(1)
        dest = os.path.join(dest, os.path.split(src)[-1])
    if os.path.exists(dest):
        print('Error: File already exists! \'%s\'' % dest)
        sys.exit(1)
    try:
        ssh.sftp.stat(src)
    except FileNotFoundError:
        print('Error: Remote file not exists! \'%s\'' % src)
        sys.exit(1)
    try:
        ssh.getfile(src=src, dest=dest)
    except PermissionError as e:
        sys.stdout.write('Error: %s!' % str(e))
        sys.exit(1)
    except Exception as e:
        sys.stdout.write('Error: %s\n' % str(e))
        sys.exit(1)
    log.info("Host: %s [Get]  src: %s  dest: %s successful" % (ssh.info[0], src, dest))
    return src, dest


def script(ssh, cf):
    if not cf['script']:
        sys.stderr.write("You must privode --script for script action! Use --help see more.\n")
        sys.stderr.flush()
        sys.exit(1)
    if ssh.info[2] == 'root':
        homePath = '/root'
    else:
        homePath = os.path.join('/home', ssh.info[2])
    if cf['script'][-1] == '/':
        sys.stderr.write("Error: --script option, You should privode file path instead of directory path.\n")
        sys.stderr.flush()
        sys.exit(2)
    if '/' in cf['script']:
        srcPath = cf['script']
        dstfile = os.path.split(srcPath)[-1]
    else:
        if os.path.exists('./%s' % cf['script']):
            srcPath = './' + cf['script']
            dstfile = os.path.split(srcPath)[-1]
        else:
            srcPath = os.path.join(cf['scripts_dir'], cf['script'])
            dstfile = cf['script']
    destPath = os.path.join(homePath, '.remotescripts/', dstfile + Utils.random())
    try:
        ssh.sftp.stat(os.path.dirname(destPath))
    except FileNotFoundError:
        try:
            ssh.sftp.mkdir(os.path.dirname(destPath))
        except PermissionError as e:
            sys.stderr('Host: %s %s' % (ssh.info[0], str(e)))
            sys.exit(2)
    cf['src'], cf['dest'] = srcPath, destPath
    if cf['append'] is None:
        cf['append'] = destPath
    else:
        if not cf['sep'] is None:
            cf['append'] = destPath + ' ' + ' '.join(cf['append'].split(cf['sep']))
        else:
            cf['append'] = destPath + ' ' + cf['append']
    put(ssh, cf)
    recode =  cmd(ssh, cf)
    ssh._ssh.exec_command("bash -c \"rm -rf {cmd}\"".format(cmd=destPath),get_pty=True)
    return recode


def doc():pass

class ParseOptions(object):
    def __init__(self, argv):
        short = 'vhH:U:P:p:t:s:c:a:d:'
        long = ['help', 'host=', 'port=', 'username=', 'password=', 'script=', 'init', 'version', 'sudo', 'sep=',
                'sudo-password=', 'connect-timeout=', 'append=', 'execute-timeout=', 'scripts-dir=', 'config=',
                'auth-timeout=', 'su=', 'su-password=', 'src=', 'dest=']
        try:
            self.options = getopt.getopt(argv, short, long)
        except getopt.GetoptError as e:
            print(str(e) + '. Use --help see more.')
            sys.exit(255)

    @staticmethod
    def usage():
        __doc__ = ('remotescript Version: {ver}\n'
                   'Get the results of the remote host execution script.\n'
                   '    \n'
                   'Usage: remotescript <action> -H <host> -U <username> -P <password> ...\n'
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
                   '    -U, --username=<username>       username to use when connecting to server. [default=root]\n'
                   '    -P, --password=<password>       Password to use when connecting to server.\n'
                   '    -p, --port=<port>               Port number to use for connecting to server. [default=22]\n'
                   '    -t, --execute-timeout=<number>  Timeout for script execution. [default=60]\n'
                   '    -s, --src                       File source path. [vaild in put and get action]\n'
                   '    -d, --dest                      File destination path. [vaild in put and get action]\n'
                   '    -a, --append=<arguments>        Pass arguments to the script or command of cmd.\n'
                   '    -c, --config=<path>             Use this config file. [default=/etc/remotescript.conf]\n'
                   '    \n'
                   '    --sep                           If use --append option, Use sep for arguments. [default=" "]\n'
                   '    --init                          Initialization config file and running environment.\n'
                   '    --sudo                          Run operations with sudo. [vaild in cmd and script action]\n'
                   '    --su                            Run operations with other user. [vaild in cmd and script action]\n'
                   '    --su-password                   If have --su option, ask for other user\'s password. [vaild in cmd and script action]\n'
                   '    --script=<script-name>          Execution this script in remote host. [vaild in script action]\n'
                   '    --scripts-dir=<abspath>         If the script name is only the filename, it will be search in this directory. [default=/usr/share/remotescripts/]\n'
                   '    --connect-timeout=<number>      Timeout for host connect. [default=10]\n'
                   '    --auth-timeout=<number>         Timeout for user authentication. [default=10]'
                   .format(ver=__version__))
        return __doc__


def main():
    Config.parseConfigFile()
    if sys.argv[1] == '--init':
        init()
        sys.exit(0)
    if len(sys.argv) < 3:
        print(ParseOptions.usage())
        sys.exit(1)
    if sys.argv[1] not in ('cmd', 'get', 'put', 'script'):
        print("Only support 'cmd' 'get' 'put' 'script' action. Use --help see more")
        sys.exit(1)
    for name, value in ParseOptions(sys.argv[2:]).options[0]:
        if name == '--init':
            init()
            sys.exit(0)
        if name in ('-h', '--help'):
            print(ParseOptions.usage())
            sys.exit(0)
        if name in ('-v', '--version'):
            print(__version__)
            sys.exit(0)
        if name in ('-c', '--config'):
            Config.config['config_file'] = value
            Config.parseConfigFile()
        if name in ('-H', '--host'):
            Config.config['ssh_host'] = value
        if name in ('-U', '--username'):
            Config.config['ssh_username'] = value
        if name in ('-P', '--password'):
            Config.config['ssh_password'] = value
        if name in ('-p', '--port'):
            Config.config['ssh_port'] = int(value)
        if name in ('-t', '--execute-timeout'):
            Config.config['ssh_execute_timeout'] = int(value)
        if name in ('-a', '--append'):
            Config.config['append'] = value
        if name in ('-s', '--src'):
            Config.config['src'] = value
        if name in ('-d', '--dest'):
            Config.config['dest'] = value
        if name == '--scripts-dir':
            Config.config['scripts_dir'] = value
        if name == '--sep':
            Config.config['sep'] = value
        if name == '--connect-timeout':
            Config.config['ssh_connect_timeout'] = int(value)
        if name == '--auth-timeout':
            Config.config['ssh_auth_timeout'] = int(value)
        if name == '--sudo':
            Config.config['sudo'] = True
        if name == '--sudo-password':
            Config.config['ssh_sudo_password'] = value
        if name == '--su':
            Config.config['su'] = value
        if name == '--su-password':
            Config.config['ssh_su_password'] = value
        if name == '--script':
            Config.config['script'] = value
    global log
    log = Utils.logConfig(Config.config['log_file'])
    if not Config.config['ssh_password']:
        Config.config['ssh_password'] = __import__('getpass').getpass(
            "Remote %s's password: " % Config.config['ssh_username'])
    ssh = SSH(hostname=Config.config['ssh_host'], username=Config.config['ssh_username'],
              password=Config.config['ssh_password'],
              timeout=Config.config['ssh_connect_timeout'], auth_timeout=Config.config['ssh_auth_timeout'])
    if sys.argv[1] == 'cmd':
        sys.exit(cmd(ssh, Config.config))
    if sys.argv[1] == 'put':
        src, dest = put(ssh, Config.config)
        print("[Put]  src: %s  dest: %s successful" % (src, dest))
        sys.exit(0)
    if sys.argv[1] == 'get':
        src, dest = get(ssh, Config.config)
        print("[Get]  src: %s  dest: %s successful" % (src, dest))
        sys.exit(0)
    if sys.argv[1] == 'script':
        sys.exit(script(ssh, Config.config))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Operation cancelled by user')
        exit(1)
