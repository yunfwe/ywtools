#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-15

# 自动配置服务器yum源
# 后期添加功能：检测源是否存在 并完成相应的源检测api

from __future__ import print_function

template = '''[base]
name=CentOS-$releasever Base
baseurl=http://192.168.4.6/yum/{issue}
enabled=1
gpgcheck=0
'''

def getIssue():
    try:
        issue = open('/etc/issue').read().split()
    except IOError as e:
        print('无法完成自动配置 请联系管理员\n错误原因: %s' % e)
        __import__('sys').exit(2)
    return ''.join(issue[0]+issue[2])

def main():
    import os
    import shutil
    os.chdir('/etc/yum.repos.d')
    files = os.listdir('.')
    if 'bak' in files:
        os.rename('bak','bak_old')
        files = os.listdir('.')
    os.mkdir('bak')
    for f in files:
        shutil.move(f,'bak')
    open('CentOS-Base.repo','w').write(template.format(issue=getIssue()))
    print('yum源更改成功 并备份原来的配置文件到/etc/yum.repos.d/bak')
    print('手动执行: "yum clean all && yum makecache && yum update" 来完成更新')

if __name__ == '__main__':
    main()