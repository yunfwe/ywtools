#!/bin/bash
# author: weiyunfei

URL="http://192.168.4.6/yum/support"
ISSUE=$(cat /etc/issue|grep CentOS|awk '{print $1$3}')
BAKDIR=bak_$(date "+%Y-%m-%d")

wget -qO- $URL |grep $ISSUE &>/dev/null
RST=$?
if [ $RST != 0 ];then
    echo "暂不支持当前发行版 请联系运维人员添加此发行版的软件源"
    return 1
fi

cd /etc/yum.repos.d/
mkdir $BAKDIR &>/dev/null
mv * $BAKDIR -f &>/dev/null
cat > CentOS-Base.repo <<END
[base]
name=CentOS- Base
baseurl=http://192.168.4.6/yum/$ISSUE
enabled=1
gpgcheck=0
END
cd -  &>/dev/null
echo "yum源更改成功 并备份原来的配置文件到/etc/yum.repos.d/$BAKDIR"
echo "手动执行: \"yum clean all && yum makecache && yum update\" 来完成更新"