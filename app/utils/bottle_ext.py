#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-02

from bottle import response

def allowOrigin(func):
    def wrap(*args, **kwargs):
        response.set_header('Access-Control-Allow-Origin','*')
        response.set_header('Access-Control-Allow-Method','*')
        return func(*args, **kwargs)
    return wrap