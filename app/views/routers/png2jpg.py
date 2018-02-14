#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-02-13

from __future__ import absolute_import,print_function

import os
import bottle
import tempfile
from PIL import Image

app = bottle.Bottle()


def png2jpg(src):
    url = tempfile.mktemp()
    Image.open(src).save(url,'jpeg')
    return url

@app.route("/")
def v_index():
    return """<form action="/png2jpg" method="post" enctype="multipart/form-data">
  选择一个png图片: <input type="file" name="upload" />
  <input type="submit" value="开始转换" />
</form>"""


@app.route("/png2jpg", method="POST")
def i_png2jpg():
    upload = bottle.request.files.get('upload')
    url = tempfile.mktemp()
    upload.save(url)
    fpath = png2jpg(url)
    # bottle.response.content_type = 'application/octet-stream'
    bottle.response.content_type = 'image/jpeg'
    bottle.response.add_header("Content-Disposition","attachment;filename=%s" % os.path.split(url)[-1]+'.jpg')
    # return bottle.static_file(fpath.split(os.path.sep)[-1],root=os.path.dirname(fpath))
    return open(fpath,'rb').read()


@app.route('/get')
def v_get():
    bottle.response.content_type = 'application/octet-stream'
    return open("D:\\Application\\ScreenToGif.exe",'rb').read()

if __name__ == '__main__':
    app.run()