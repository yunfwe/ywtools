#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2018-06-08

import re
import requests
import yagmail
from time import sleep
from time import strftime

# mails = ['1441923087@qq.com','996906881@qq.com','liliming1976@sina.com']
mails = ['1441923087@qq.com']
temperatureMax = 30
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
    url = 'http://172.16.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/login.aspx'
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
        'Origin': 'http://172.16.0.251',
        'Referer': 'http://172.16.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/login.aspx',
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
        '258843952','438476297','1076765387','124220196',
        '356956543','470925726','438476297','226663635',
        '323855602','303328253'
    ]
    shidu = [
        '662128479','640315570','1078928075','527504723',
        '760241070','874210253','841760824','727140129',
        '706612780','629948162'
    ]
    url = 'http://172.16.0.251:9999/ActiveDataService/'
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
        'Referer':'http://172.16.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/ClientBin/SolarWeb.xap',
        'Content-type': 'text/xml',
        'Accept-Language': 'zh-CN',
        'Host': '172.16.0.251:9999',
        'Connection': 'Keep-Alive',
        'Pragma': 'no-cache',
        'SOAPAction': '"http://www.mgrid.com.cn/IActiveDataService/BatchDataProcess"'
    }
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><data xmlns="www.mgrid.com">-1</data></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><BatchDataProcess xmlns="http://www.mgrid.com.cn/"><requests><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:8-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:8-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:9-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:9-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:10-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:10-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:11-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:11-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:12-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:12-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:13-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:13-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:14-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:14-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:15-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:15-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:16-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:16-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:17-Temp:171-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:17-Temp:171-Signal:2]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[State[Equip:6]]}|#FF00FF00&amp;#FFFF0000&amp;#FF0000FF</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[State[Equip:7]]}|#FF00FF00&amp;#FFFF0000&amp;#FF0000FF</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[State[Equip:19]]}|#FF00FF00&amp;#FFFF0000&amp;#FF0000FF</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[State[Equip:18]]}|#FF00FF00&amp;#FFFF0000&amp;#FF0000FF</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain></requests></BatchDataProcess></s:Body></s:Envelope>'
    tmp = opener.post(url,data=data, headers=headers).text
    result = ''
    for i in valMap.items():
        val = re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i[0],tmp)
        result += i[1][0]+':\t'+val[0]+' '+i[1][1]+'\n'
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

def getMachine1Status():
    valMap = {
        '754223481': ['室内温度','°C'],
        '747735417': ['屋内湿度','%RH'],
        '2918514': ['加湿设定值','%RH'],
        '361311562': ['除湿设定值', '%RH'],
        '-1194221083': ['冷却设定值', '°C'],
        '-1564541683': ['系统风机状态',''],
        '-1161257156': ['压缩机状态','']
    }
    url = 'http://172.16.0.251:9999/ActiveDataService/'
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
        'Referer':'http://172.16.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/ClientBin/SolarWeb.xap',
        'Content-type': 'text/xml',
        'Accept-Language': 'zh-CN',
        'Host': '172.16.0.251:9999',
        'Connection': 'Keep-Alive',
        'Pragma': 'no-cache',
        'SOAPAction': '"http://www.mgrid.com.cn/IActiveDataService/BatchDataProcess"'
    }
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><data xmlns="www.mgrid.com">-1</data></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><BatchDataProcess xmlns="http://www.mgrid.com.cn/"><requests><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:95]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:93]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:94]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:96]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:98]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:99]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:100]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:101]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Name[Equip:6]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:6]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:81]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:82]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:83]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:84]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:85]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:1]]}</EX><RT>2</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:68]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:70]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:19]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:86]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:87]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:88]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:89]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:6-Temp:174-Signal:90]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:6-Temp:174-Signal:109]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain></requests></BatchDataProcess></s:Body></s:Envelope>'
    tmp = opener.post(url,data=data, headers=headers).text
    result = ''
    for i in valMap.items():
        val = re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i[0],tmp)
        result += i[1][0]+':\t'+val[0]+' '+i[1][1]+'\n'
    return result

def getMachine2Status():
    valMap = {
        '-2111750515': ['室内温度','°C'],
        '-2036398229': ['屋内湿度','%RH'],
        '-2068754412': ['加湿设定值','%RH'],
        '1872145212': ['除湿设定值', '%RH'],
        '316612567': ['冷却设定值', '°C'],
        '-907331254': ['系统风机状态',''],
        '658752687': ['压缩机状态','']
    }
    url = 'http://172.16.0.251:9999/ActiveDataService/'
    headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
        'Referer':'http://172.16.0.251/monitor/(S(dsz4zpnq3tbnpofmk0jznprr))/ClientBin/SolarWeb.xap',
        'Content-type': 'text/xml',
        'Accept-Language': 'zh-CN',
        'Host': '172.16.0.251:9999',
        'Connection': 'Keep-Alive',
        'Pragma': 'no-cache',
        'SOAPAction': '"http://www.mgrid.com.cn/IActiveDataService/BatchDataProcess"'
    }
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><data xmlns="www.mgrid.com">-1</data></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><BatchDataProcess xmlns="http://www.mgrid.com.cn/"><requests><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:1]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:95]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:93]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:94]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:96]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:98]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:99]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:100]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:101]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Name[Equip:7]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:6]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:81]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:82]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:83]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:84]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:85]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:1]]}</EX><RT>2</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:68]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:70]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:19]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:86]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:87]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:88]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:89]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[Value[Equip:7-Temp:174-Signal:90]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain><RequestDomain xmlns="www.mgrid.com"><EX>Binding{[EventSeverity[Equip:7-Temp:174-Signal:109]]}</EX><RT>1</RT><TAG xsi:nil="true" /></RequestDomain></requests></BatchDataProcess></s:Body></s:Envelope>'
    tmp = opener.post(url,data=data, headers=headers).text
    result = ''
    for i in valMap.items():
        val = re.findall(r'%s</a:HashCode><a:Value>(.*?)</a:Value>' % i[0],tmp)
        result += i[1][0]+':\t'+val[0]+' '+i[1][1]+'\n'
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
                tmp += '\n空调1\n'+getMachine1Status()
                tmp += '\n空调2\n'+getMachine2Status()
                tmp += '\n\n当前第%s次发送，最多发送%s次。' % (send_count,maxcount)
                sendmail(sub='警报：机房温度过高！！！当前最高温度：%s' % currentTemperature, content=tmp)
                if send_count == maxcount:
                    isNotice = True
                    send_count = 0
            print('['+now()+'] 当前最高区域温度：'+str(currentTemperature)+' 限制最高：'+str(temperatureMax))
        except:
            time.sleep(60)
        sleep(period)


if __name__ == '__main__':
    main()