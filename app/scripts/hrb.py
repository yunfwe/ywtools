#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-06-14

import re
import requests
from time import sleep
from time import strftime

mails = ['1441923087@qq.com','996906881@qq.com','liliming1976@sina.com']
#mails = ['1441923087@qq.com']
temperatureMax = 32
currentTemperature = 0
period = 600

def sendmail(sub=None,content=None):
    global mails
    yag = yagmail.SMTP(user='18801458581@163.com', password='sdxz_2015',
                       host='smtp.163.com', port='25',smtp_ssl=False)
    yag.send(to=mails,subject=sub,
             contents=content)
    print("邮件发送成功")
    yag.close()

now = lambda :strftime('%Y-%m-%d %H:%M:%S')

opener = requests.Session()


def login():
    url = 'http://172.17.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/login.aspx'
    data = {
        '__VIEWSTATE': '/wEPDwUKLTg0MjAwMjc1NQ9kFgICAw9kFgICAw9kFgICAQ8WAh4JaW5uZXJodG1sBRjmnLrmiL/nm5HmjqfnrqHnkIblubPlj7BkZMO2IlxtLbahLne+3eri5ElAhHrvOw7eaevahPNVQKSs',
        '__EVENTVALIDATION': '/wEWBALm5LzXBgKl1bKzCQK1qbT2CQLL9rEEzELnwhCSsXwh9VLY2eDsRmUhlUjyRFB1mmO6evwwtSY=',
        'txtUserName': 'admin',
        'txtpassword': 'admin',
        'hhead': '696'
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '311',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': '172.16.0.251',
        'Origin': 'http://172.17.0.251',
        'Referer': 'http://172.17.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/login.aspx',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
    }
    opener.post(url, data=data, headers=headers)

def getTemperature():
    global currentTemperature
    valMap = {
        '258843952': ['备门温度','°C'],
        '662128479': ['备门湿度','%RH'],
        '226663635': ['UPS附近温度','°C'],
        '629948162': ['UPS附近湿度','%RH'],
        '1076765387': ['主门温度','°C'],
        '1078928075': ['主门湿度','%RH'],
    }
    temperature = [
        '258843952','470925726','303193848','438476297','356956543','303328253',
        '323855602','226663635','124220196','1774560406','393405855','1954192751',
        '1986642180','1872672997','1639936650','1819044707'
    ]
    shidu = [
        '662128479','841760824','874210253','760241070','527504723','706612780','727140129',
        '629948162','100090679','9878672','208476465','388108810','420558239','306589056',
        '73852709','252960766'
    ]
    url = 'http://172.17.0.251:9999/ActiveDataService/'
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
        'Referer':'http://172.17.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/ClientBin/SolarWeb.xap',
        'Content-type': 'text/xml',
        'Accept-Language': 'zh-CN',
        'Host': '172.17.0.251:9999',
        'Connection': 'Keep-Alive',
        'Pragma': 'no-cache',
        'SOAPAction': '"http://www.mgrid.com.cn/IActiveDataService/BatchDataProcess"'
    }
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><data xmlns="www.mgrid.com">-1</data></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><BatchDataProcess xmlns="http://www.mgrid.com.cn/"><requests><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:10-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:10-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:26-Temp:175-Signal:10]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:11-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:11-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:12-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:12-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:13-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:13-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:15-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:15-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:14-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:14-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:16-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:16-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:17-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:17-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:18-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:18-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:19-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:19-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:26-Temp:175-Signal:11]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:26-Temp:175-Signal:12]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:20-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:20-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:21-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:21-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:25-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:25-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:24-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:24-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:22-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:22-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:23-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:23-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:4]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:3]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:5]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:6]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:7]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:26-Temp:175-Signal:8]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:26-Temp:175-Signal:13]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain></requests></BatchDataProcess></s:Body></s:Envelope>'
    tmp = opener.post(url,data=data, headers=headers).text
    result = ''
    # for i in valMap.items():
    #     val = re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i[0],tmp)
    #     result += i[1][0]+':\t'+val[0]+' '+i[1][1]+'\n'
    temp = []
    sd = []
    for i in temperature:
        temp.append(float(re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i,tmp)[0]))
    for i in shidu:
        sd.append(float(re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i,tmp)[0]))
    result += '\n整体温度最高： %s°\t最低: %s°\t平均: %.3f°\n' % (str(max(temp)),str(min(temp)),sum(temp)/len(temp))
    result += '整体湿度最高： %s\t最低: %s\t平均: %.3f\n' % (str(max(sd)),str(min(sd)),sum(sd)/len(sd))
    currentTemperature = max(temp)
    return result


def main():
    global currentTemperature,temperatureMax,period
    send_count = 0
    maxcount = 3
    isNotice = False
    while True:
        try:
            login()
            tmp = '温度\n'
            tmp += getTemperature()
            if currentTemperature <= temperatureMax and isNotice:
                isNotice = False
                send_count = 0
            if currentTemperature >= temperatureMax and not isNotice:
                send_count += 1
                tmp += '\n\n当前第%s次发送，最多发送%s次。' % (send_count,maxcount)
                sendmail(sub='警报：哈尔滨机房温度过高！！！当前最高温度：%s' % currentTemperature, content=tmp)
                if send_count == maxcount:
                    isNotice = True
                    send_count = 0
            print('['+now()+'] 当前哈尔滨机房最高区域温度：'+str(currentTemperature)+' 限制最高：'+str(temperatureMax))
        except:
            sleep(60)
        sleep(period)

def printinfo():
    login()
    tmp = '<h2>哈尔滨</h2>温度\n'
    tmp += getTemperature()
    return tmp.replace('\n','<br/>')


if __name__ == '__main__':
    main()
