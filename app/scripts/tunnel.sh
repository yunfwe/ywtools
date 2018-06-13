#!/bin/bash  
### BEGIN INIT INFO
# Provides:          weiyunfei
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: udp tunnel
# Description:       udp tunnel
### END INIT INFO
  
## Fill in name of program here.  
PROG="tunclient.py"  
PROG_PATH="/usr/local/bin" ## Not need, but sometimes helpful (if $PROG resides in /opt for example).  
PROG_ARGS="47.104.178.134 2003 -d"   
PID_PATH="/var/run/"  

while :;do
    /usr/local/bin/tunclient.py 47.104.178.134 2003 &>/dev/null
    sleep 3
done &
