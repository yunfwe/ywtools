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
  
start() {  
    if [ -e "$PID_PATH/$PROG.pid" ]; then  
        ## Program is running, exit with error.  
        echo "Error! $PROG is currently running!" 1>&2  
        exit 1  
    else  
        ## Change from /dev/null to something like /var/log/$PROG if you want to save output.  
        $PROG_PATH/$PROG $PROG_ARGS 2>&1 >/var/log/$PROG &  
        pid=`ps aux |grep tunclient.py|grep -v 'grep'|head -n1|awk '{print $2}'`  
  
        echo "$PROG started"  
        echo $pid > "$PID_PATH/$PROG.pid"  
    fi  
}  
  
stop() {  
    echo "begin stop"  
    if [ -e "$PID_PATH/$PROG.pid" ]; then  
        ## Program is running, so stop it  
        pid=`ps aux |grep tunclient.py|grep -v 'grep'|head -n1|awk '{print $2}'`  
        kill $pid
        rm -f  "$PID_PATH/$PROG.pid"  
        echo "$PROG stopped"  
    else  
        ## Program is not running, exit with error.  
        echo "Error! $PROG not started!" 1>&2  
        exit 1  
    fi  
}  
  
  
case "$1" in  
    start)  
        start  
        exit 0  
    ;;  
    stop)  
        stop  
        exit 0  
    ;;  
    reload|restart|force-reload)  
        stop  
        start  
        exit 0  
    ;;  
    **)  
        echo "Usage: $0 {start|stop|reload}" 1>&2  
        exit 1  
    ;;  
esac  
