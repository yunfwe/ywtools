#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-09-21

from __future__ import absolute_import,print_function

from gevent import monkey;monkey.patch_all()

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import bottle
import time

app = bottle.Bottle()

@app.route('/')
def index():
    for i in range(10):
        time.sleep(1)
        yield str(i)+'\r\n'
    # print('IDRAC Control')

@app.route('/echo')
def echo():
    ws = bottle.request.environ.get('wsgi.websocket')
    while True:
        msg = ws.receive()
        ws.send('Hello: '+msg)

if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), application=app, handler_class=WebSocketHandler)
    server.serve_forever()