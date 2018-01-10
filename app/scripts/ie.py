#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gevent import monkey; monkey.patch_time()
from gevent.pywsgi import WSGIServer

import os
import time
import bottle
import traceback
import yagmail
import threading
from PIL import ImageGrab
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def sendmail(sub=None,content=None):
    if sub is None:
        sub = "北京和哈尔滨机房视频监控及环控截图"
    if content is None:
        content = ['北京机房视频','bjvideo.jpeg',
                   '哈尔滨机房视频','hrbvideo.jpeg',
                   '北京环控','bjhk.jpeg',
                   '哈尔滨环控','hrbhk.jpeg','访问：http://172.16.11.4/screen 手动触发']
    mails = ['1441923087@qq.com','yung241088@126.com','liliming1976@sina.com']
    #mails = '1441923087@qq.com'
    yag = yagmail.SMTP(user='18600361043@163.com', password='mkxdzhzz199709',
                       host='smtp.163.com', port='25',smtp_ssl=False)
    yag.send(to=mails,subject=sub,
             contents=content)
    yag.close()


def screen(retries=None):
    ie = webdriver.Ie()
    if retries is None:retries = 3
    try:
        # 北京机房视频监控
        URL = "http://172.16.0.252/"
        ie.maximize_window()
        # raise KeyError("hehehe")
        time.sleep(5)
        ie.get(URL)
        user = ie.find_element_by_id("szUserName")
        user.send_keys("admin")
        passwd = ie.find_element_by_id("szUserPasswdSrc")
        passwd.send_keys("Admin88")
        passwd.send_keys(Keys.RETURN)
        time.sleep(5)
        ie.execute_script('$("#container").contents().find("#batchSwitch").click()')
        time.sleep(20)
        ImageGrab.grab().save('bjvideo.jpeg','jpeg')
        #ie.save_screenshot('bjvideo.png')

        # 哈尔滨机房视频监控
        URL = "http://172.17.0.252/"
        ie.get(URL)
        user = ie.find_element_by_id("szUserName")
        user.send_keys("admin")
        passwd = ie.find_element_by_id("szUserPasswdSrc")
        passwd.send_keys("Admin88")
        passwd.send_keys(Keys.RETURN)
        time.sleep(5)
        ie.execute_script('$("#container").contents().find("#batchSwitch").click()')
        time.sleep(20)
        ImageGrab.grab().save('hrbvideo.jpeg','jpeg')
        #ie.save_screenshot('hrbvideo.png')

        # 北京环控
        URL = "http://172.16.0.251/monitor"
        ie.get(URL)
        user = ie.find_element_by_id("txtUserName")
        user.send_keys("admin")
        passwd = ie.find_element_by_id("txtpassword")
        passwd.send_keys("admin")
        passwd.send_keys(Keys.RETURN)
        time.sleep(20)
        ImageGrab.grab().save('bjhk.jpeg','jpeg')
        #ie.save_screenshot('bjhk.png')

        # 哈尔滨环控
        URL = "http://172.17.0.251/monitor"
        ie.get(URL)
        user = ie.find_element_by_id("txtUserName")
        user.send_keys("admin")
        passwd = ie.find_element_by_id("txtpassword")
        passwd.send_keys("admin")
        passwd.send_keys(Keys.RETURN)
        time.sleep(60)
        ImageGrab.grab().save('hrbhk.jpeg','jpeg')
        #ie.save_screenshot('hrbhk.png')
        sendmail()
        os.remove("bjvideo.jpeg")
        os.remove("hrbvideo.jpeg")
        os.remove("bjhk.jpeg")
        os.remove("hrbhk.jpeg")
        ie.close()
    except Exception as e:
        if retries > 0:
            ie.close()
            retries -= 1
            screen(retries)
        else:
            ImageGrab.grab().save('IE.jpeg','jpeg')
            ie.close()
            time.sleep(3)
            ImageGrab.grab().save('CMD.jpeg','jpeg')
            sendmail(sub="监控出错了！",content=[traceback.format_exc(),'IE.jpeg','CMD.jpeg','\n访问 http://172.16.11.4/screen 手动触发'])
            os.remove("IE.jpeg")
            os.remove("CMD.jpeg")


app = bottle.Bottle()

@app.route("/screen")
def v_screen():
    if len(threading.enumerate())>1:
        return "任务正在进行中...大概需要几分钟"
    threading.Thread(target=screen).start()
    return "截图工作已在后台开始 请等待邮件"


bind = ('0.0.0.0',80)
server = WSGIServer(bind,app)
print('Server listen on %s:%s\n' % bind)
server.serve_forever()

