#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-15

import os
from bottle import Bottle

share = Bottle()

# @share.route('/getAllFiles')
def v_getAllFiles():
    nodes = []
    path = '/usr/local/nginx/'
    for root,dir,fis in os.walk(path):
        for d in dir:
            nodes.append()


nodes = []
def walk(root,):
    pass


if __name__ == '__main__':
    print(v_getAllFiles())