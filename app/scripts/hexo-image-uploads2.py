#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-02-07

import os
import time
import random
import pyperclip
from PIL import ImageGrab,Image
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication


app = QApplication([])
clipboard = QApplication.clipboard()



def makeRandomNum(size=16):
    num = list(range(48,58))+list(range(48,58))
    char = list(range(97,123))
    return ''.join(map(chr,[random.choice(num+char) for _ in range(size)]))

def getImageClipboard(dst=''):
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        fn = makeRandomNum()+'.jpeg'
        im.save(os.path.join(dst,fn), 'jpeg',quality=20)
        index = dst.split('\\').index('uploads')
        url = '/'+'/'.join(dst.split('\\')[index:])+'/'
        pyperclip.copy('![](%s)\n'%(url+fn))
        print('![](%s)'%(url+fn))

def on_clipboard_change():
    data = clipboard.mimeData()
    dst = open("hexo-image-uploads.conf").read()
    if data.hasImage():
        getImageClipboard(dst)
    if data.hasFormat('text/uri-list'):
        index = dst.split('\\').index('uploads')
        url = '/'+'/'.join(dst.split('\\')[index:])+'/'
        a = data.urls()[0].toString()
        src = a.split('///')[1]
        fm = src.split('.')[-1]
        if fm not in ['gif','png','jpeg','jpg','bmp','webp']:
            print('不是图片格式 pass')
            return 
        f = makeRandomNum()
        fn = f+'.'+fm
        nn = f+'.'+'jpeg'
        Image.open(src).save(os.path.join(dst,nn),'jpeg', quality=20)
        pyperclip.copy('![](%s)\n'%(url+fn))
        print('![](%s)'%(url+fn))
        


def main():
    print("开始监听剪切板")
    clipboard.dataChanged.connect(on_clipboard_change)
    app.exec_()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    


