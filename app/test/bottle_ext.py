#!/usr/bin/env python

import bottle

def allowOrgin(method='*'):
    def _allowOrgin(callback):
        def wrapper(*args, **kwargs):
            bottle.response.set_header('Access-Control-Allow-Origin','*')
            bottle.response.set_header('Access-Control-Allow-Method',method)
            bottle.response.set_header('bottle','allowOrgin')
            return callback(*args, **kwargs)
        return wrapper
    return _allowOrgin

app = bottle.Bottle()
# app.install(allowOrgin())

@app.route('/json')
def json():
    return {"a":"1"}

@app.route('/json2', apply=[allowOrgin(),])
@app.route('json3')
def json2():
    return {"a":"2"}

app.run()