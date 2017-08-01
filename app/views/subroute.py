#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-26

import bottle

sub = bottle.Bottle()

@sub.route('/subroute')
def v_sub():
    return 'subroute'