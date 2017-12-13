#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-12-13

import sys
import yagmail

yag = yagmail.SMTP(user='18600361043@163.com', password='mkxdzhzz199709',
                   host='smtp.163.com', port='25',smtp_ssl=False)
content = sys.argv[3]
open('/tmp/mail.log','a').write(content+'\n\n\n\n')
content = content.replace('\\n','\n')
yag.send(to=sys.argv[1],subject=sys.argv[2], contents=[content])

