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

mails = ['1441923087@qq.com','996906881@qq.com','liliming1976@sina.com']

def sendmail_bak(sub=None,content=None):
    global mails
    if sub is None:
        sub = "北京和哈尔滨机房视频监控及环控截图"
    if content is None:
        content = ['北京机房视频','bjvideo.jpeg',
                   '哈尔滨机房视频','hrbvideo.jpeg',
                   '北京环控','bjhk.jpeg',
                   '哈尔滨环控','hrbhk.jpeg','访问：http://172.16.11.4/screen 手动触发']
    #mails = '1441923087@qq.com'
    yag = yagmail.SMTP(user='18801458581@163.com', password='sdxz_2015',
                       host='smtp.163.com', port='25',smtp_ssl=False)
    yag.send(to=mails,subject=sub,
             contents=content)
    print("邮件发送成功")
    yag.close()

def sendmail():
    global mails
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.header import Header
    from email.utils import parseaddr, formataddr
    body = """
    <h1>北京机房视频监控</h1>
    <img src="cid:image1"/>
    <h1>哈尔滨机房视频监控</h1>
    <img src="cid:image2"/>
    <h1>北京机房环境温度监控</h1>
    <img src="cid:image3"/>
    <h1>哈尔滨机房环境温度监控</h1>
    <img src="cid:image4"/>
    <h1>访问：http://172.16.11.4/screen 手动触发<h1>
    """
    smtp_server = 'smtp.163.com'
    from_mail = '18801458581@163.com'
    mail_pass = 'sdxz_2015'
    to_mail = mails
    # 构造一个MIMEMultipart对象代表邮件本身
    msg = MIMEMultipart() 
    # Header对中文进行转码
    msg['From'] = from_mail
    msg['To'] = ','.join(to_mail)
    msg['Subject'] = Header('北京和哈尔滨机房视频监控及环控截图', 'utf-8').encode()
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    # 二进制模式读取图片
    with open('bjvideo.jpeg', 'rb') as f:
        msgImage1 = MIMEImage(f.read())
    with open('hrbvideo.jpeg', 'rb') as f:
        msgImage2 = MIMEImage(f.read())
    with open('bjhk.jpeg', 'rb') as f:
        msgImage3 = MIMEImage(f.read())
    with open('hrbhk.jpeg', 'rb') as f:
        msgImage4 = MIMEImage(f.read())
    # 定义图片ID
    msgImage1.add_header('Content-ID', '<image1>')
    msg.attach(msgImage1)
    msgImage2.add_header('Content-ID', '<image2>')
    msg.attach(msgImage2)
    msgImage3.add_header('Content-ID', '<image3>')
    msg.attach(msgImage3)
    msgImage4.add_header('Content-ID', '<image4>')
    msg.attach(msgImage4)
    try:
        s = smtplib.SMTP()     
        s.connect(smtp_server, "25")   
        s.login(from_mail, mail_pass)
        s.sendmail(from_mail, to_mail, msg.as_string())  # as_string()把MIMEText对象变成str     
        s.quit()
    except smtplib.SMTPException as e:
        print("Error: %s" % e)

def screen(retries=None):
    #ie = webdriver.Ie()
    if retries is None:retries = 3
    try:
        # 北京机房视频监控
        URL = "http://172.16.0.252/"
        #ie.close()
        ie = webdriver.Ie()
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
        os.popen("taskkill /f /im iexplore.exe").read()
        ie = webdriver.Ie()
        ie.maximize_window()
        time.sleep(5)
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
        os.popen("taskkill /f /im iexplore.exe").read()
    except Exception as e:
        print(str(e))
        if retries > 0:
            os.popen("taskkill /f /im iexplore.exe").read()
            retries -= 1
            screen(retries)
        else:
            ImageGrab.grab().save('IE.jpeg','jpeg')
            os.popen("taskkill /f /im iexplore.exe").read()
            time.sleep(3)
            ImageGrab.grab().save('CMD.jpeg','jpeg')
            sendmail_bak(sub="监控出错了！",content=[traceback.format_exc(),'IE.jpeg','CMD.jpeg','\n访问 http://172.16.11.4/screen 手动触发'])
            os.remove("IE.jpeg")
            os.remove("CMD.jpeg")

def main():
    app = bottle.Bottle()

    @app.route("/screen")
    def v_screen():
        if len(threading.enumerate())>1:
            return "任务正在进行中...大概需要几分钟\n"
        threading.Thread(target=screen).start()
        return "截图工作已在后台开始 请等待邮件\n"

    @app.route("/reboot")
    def v_reboot():
        os.popen("shutdown -r -t 0")
        return "正在重启\n"


    bind = ('0.0.0.0',80)
    server = WSGIServer(bind,app)
    print('Server listen on %s:%s\n' % bind)
    server.serve_forever()

if __name__ == '__main__':
    main()



