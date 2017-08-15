#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-08-15

import gevent.monkey;gevent.monkey.patch_all()

from bottle import Bottle
from app.views.routers.webapi import api

app = Bottle()
app.mount('/api/', api)

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(("0.0.0.0", 8080), app,
                        handler_class=WebSocketHandler)
    server.serve_forever()