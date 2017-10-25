#!/usr/bin/python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-10-24

import os
import sys
import time
import signal
import logging
import commands

import pyinotify


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [usbAutoMount] %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/var/log/usbAutoMount.log',
                    filemode='a')


def checkusb(devname='/dev/sda1'):
    return os.path.exists(devname)

def mountusb(devname='/dev/sda1',target='/mnt/usb'):
    if not os.path.exists(target): os.mkdir(target)
    rst = commands.getstatusoutput('/bin/mount %s %s' % (devname,target))
    if rst[0] != 0:
        logging.error(rst[1])
        return False
    logging.info('mount %s success' % target)
    return True

def umountusb(target='/mnt/usb'):
    os.popen('/bin/fuser -ka %s' % target).read()
    rst = commands.getstatusoutput('/bin/umount %s' % target)
    if rst[0] != 0:
        logging.error(rst[1])
        return False
    logging.info('umount %s success' % target)
    return True

class leds(object):
    @staticmethod
    def on():
        open("/dev/leds_ctl",'w',buffering=False).write('1')

    @staticmethod
    def off():
        open("/dev/leds_ctl",'w',buffering=False).write('0')

leds.off()

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if event.name != 'sda1':return
        logging.info("Found file: %s " %  os.path.join(event.path,event.name))
        if not mountusb():return
        leds.on()
        logging.info('now running mysql backup process...')
        rst = commands.getstatusoutput(open('/etc/usbAutoMount.conf').readlines()[0].strip())
        logging.info('mysql backup process run done')
        logging.info('mysql backup process: rc: %s msg: %s' % rst)
        time.sleep(3)
        umountusb()
        leds.off()


    def process_IN_DELETE(self, event):
        if event.name != 'sda1':return
        logging.info("Delete file: %s " %  os.path.join(event.path,event.name))
        leds.off()

def fsmonitor(path='/dev'):
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE 
    notifier = pyinotify.Notifier(wm, EventHandler())
    wm.add_watch(path, mask,auto_add=True,rec=True)
    logging.info('starting monitor %s'%(path))
    def safestop(signum, frame):
        notifier.stop()
        logging.info('stopped monitor %s'%(path))
        sys.exit(0)
    signal.signal(15, safestop)
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except Exception as e:
            logging.error(str(e))
            notifier.stop()
            logging.info('stopped monitor %s'%(path))
            break

if __name__ == "__main__":
    try:
        if sys.argv[1] == 'daemon':
            pid = os.fork()
            if pid != 0:sys.exit(0)
    except IndexError:pass
    try:
        fsmonitor()
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
