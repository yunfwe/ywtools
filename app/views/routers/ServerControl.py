#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-16

from bottle import Bottle

sc = Bottle()

@sc.route('/<action>/<name>')
def v_contorl(action, name):
    return action+name