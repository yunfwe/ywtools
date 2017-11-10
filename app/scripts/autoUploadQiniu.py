#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-11-10

"""
对某个目录进行监听
如果有新增的文件 判断是否为图片格式
如果是图片格式 上传到七牛云 获取外链
图片名和外链写入到一个索引文件中
将外链写入到粘贴板
"""

import os
import time
import json
import pyperclip
from PIL import ImageGrab
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from qiniu import Auth, put_file

app = QApplication([])
config = json.loads(open('config.json').read())


cache_dir = config['cache_dir']
bucket_name = config['bucket_name']
domain = config['domain']
if not domain.endswith('/'):domain += '/'
ak = config['access_key']
sk = config['secret_key']
ocp = config['auto_copy_url']

if not os.path.exists(cache_dir): os.mkdir(cache_dir)

def upload(fn):
    key = os.path.split(fn)[-1]
    q = Auth(ak, sk)
    token = q.upload_token(bucket_name, key)
    rst,info = put_file(token, key, fn)


rdm = lambda :str(int(time.time()*1000))


def imgsave(fn):
    img = ImageGrab.grabclipboard()
    img.save(fn, "png")


clipboard = app.clipboard()
def on_clipboard_change():
    data = clipboard.mimeData()
    if data.hasImage():
        fn = rdm()+'.png'
        fnp = os.path.join(cache_dir,fn)
        imgsave(fnp)
        upload(fnp)
        url = '![](%s)\n'%(domain + fn)
        if ocp == 'true':
            pyperclip.copy(url)
        open(os.path.join(cache_dir,'index.txt'),'a').write(fn+'\t'+url)
        print(fn+'\t'+url,sep='')

clipboard.dataChanged.connect(on_clipboard_change)
app.exec_()