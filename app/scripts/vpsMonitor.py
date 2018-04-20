#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-04-04

import re
import time
import requests
import yagmail

url = "https://www.bwh1.net/vps-hosting.php"

def monitor():
    data = requests.get(url).text
    rst = re.findall(r"<div class='bronze'>.*?</div>",data,re.S)
    rst = re.split(r'<.*?>',rst[0])
    rst = list(filter(lambda x:len(x)>1 and x[0]!='&',rst))
    if 'KVM: no stock' not in rst:
        return True
    return False

try:
    while True:
        if monitor():
            try:
                yag = yagmail.SMTP(user='18801458581@163.com', password='sdxz_2015',
                                   host='smtp.163.com', port=587,smtp_ssl=True)
                yag.send(to=['1441923087@qq.com'],
                         subject="办哇公有主机了", contents=['到办哇公主页购买'])
                open('info.log','a').write('发送成功')
            except:
                open('info.log','a').write('发送失败')
            exit(0)
        else:
            open('info.log','a').write(str(time.time())+'\n')
            time.sleep(600)
except:
    pass