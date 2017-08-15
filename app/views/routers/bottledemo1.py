#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-25

from __future__ import absolute_import
from __future__ import print_function

from gevent import monkey;

monkey.patch_all()
import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import time
import subprocess
from bottle import Bottle, request, static_file, abort, redirect, response
from app.views.routers.subroute import sub



app = Bottle()
app.mount('/blog',sub)
@app.route('/', method='ANY')
def v_main():
    for i in range(10):
        yield 'hello world</br>\n'
        time.sleep(1)
    # return {'a':1}
    # return request.method+'\n'

@app.route('/infomation')
@app.route('/info/<name>', template='info')
def v_info(name):
    # return name
    response.set_header('Access-Control-Allow-Origin','*')
    response.set_header('Access-Control-Allow-Method','*')
    # if request.get_cookie('username',secret='~,f,093h08*@od'):
    #     return 'Hello %s' % request.get_cookie('username',secret='~,f,093h08*@od')
    response.set_cookie('username','hahaha', secret='~,f,093h08*@od')
    # return template('info', {'name':name, 'age':1})
    return {'name':name, 'age':1}

@app.route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath,root='/')

@app.route('/baidu')
def dir_baidu():
    redirect('http://www.baidu.com')

@app.route('/404')
def abort_404():
    abort(404)

@app.route('/docker')
def v_docker():
    return '''<form action="/dockerupload" method="post" enctype="multipart/form-data">
  File: <input type="file" name="upload" />
  <input type="submit" value="Start upload" />
</form>
'''

@app.route('/dockerupload', method='post')
def v_dockerupload():
    df = request.files.get('upload')
    # f  = open('/tmp/'+df.filename, 'wb')
    # while True:
    #     data = df.file.read(40960)
    #     if not data:break
    #     f.write(data)
    # f.close()
    dp = subprocess.Popen(["docker load"], shell=True, stdin=df.file, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdo, stde = dp.communicate()
    if stde:return stde
    return '导入成功'

@app.route('/item<item:re:[0-9]+>')
def v_item(item):
    return item

@app.route('/websocket')
def handle_websocket():
    ws = request.environ.get('wsgi.websocket')
    if not ws:abort(400, 'Expected WebSocket request.')
    processList = []
    def send():
        p = subprocess.Popen(['ping 192.168.8.254'],shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        processList.append(p)
        data = p.stdout.readline()
        while data:ws.send(data)
    def recv():
        while True:
            message = ws.receive()
            p = processList[-1]
            print(message)
            if message == 'stop':
                p.terminate()
    gevent.joinall([
        gevent.spawn(send),
        gevent.spawn(recv)
    ])
    ws.close()

if __name__ == '__main__':
    # run(server='gevent',app=app, host='0.0.0.0', port=8080, debug=True, reloader=True)
    server = WSGIServer(('0.0.0.0',8080), application=app, handler_class=WebSocketHandler)
    server.serve_forever()