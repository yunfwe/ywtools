#!/usr/bin/env python
# coding:utf-8

import re
import sys
import requests

# url = 'https://www.shanbay.com/wordlist/187711/540709/?page=%s'


def parse(page=1):
    text = requests.get(url % str(page)).text
    tmp = re.findall(r'<table class="table table-bordered table-striped">\s*<tbody>(.*?)</tbody>.*</table>', text, re.S)
    return re.findall(r'<strong>(.*?)</strong>.*?<td class="span10">(.*?)</td>', text, re.S)

if __name__ == '__main__':
    for a in range(540709,540796,3):
        url = 'https://www.shanbay.com/wordlist/187711/'+str(a)+'/?page=%s'
        for i in range(1,20):
            data = parse(i)
            if not data: break
            for k,v in data:
                open('python.txt','a').write(k.ljust(16)+' '.join(v.split())+'\n')
                open('pythonw.txt','a').write(k+'\n')
        print(url+'\tOK')