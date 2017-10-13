#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Create: 2016-08-26 10:33:35  Author: weiyunfei

from __future__ import print_function
# from __future__ import unicode_literals

import os
import sys
import time
import json
import getopt
import socket
import tarfile
import hashlib
import subprocess
import random as rand
from tempfile import mktemp
from os.path import getsize
from base64 import b64decode
from shutil import copy,move,rmtree

busybox = ''''''

PATH = os.getcwd()

global SETTING

def config():
    import ConfigParser
    configPath = ['./mdrs.conf',os.environ.get('HOME')+'/.mdrs.conf','/etc/mdrs.conf']
    configContext = "[global]\nlog = /tmp/mdrs.log\n\n[register]\nlisten = 0.0.0.0\nport = 11190\npid = /var/run/mdrs.pid\nworkdir = /var/image/\n\n[client]\n# support HTTP address\nserver = mdrs://127.0.0.1:11190\n"
    
    for i in configPath:
        if os.path.exists(i):
            config = i
            break
        else:
            config = None
            
    if config == None:
        open(configPath[1],'w').write(configContext)
        config = configPath[1]
        print('Initialization config file success! Path: %s' % configPath[1])
        print('Please edit server address first!')
        sys.exit(0)
        
    cf = ConfigParser.ConfigParser() 
    cf.read(config)
    setting = {}
    for i in cf.sections():
        setting[i] = dict(cf.items(i))
    return setting

SETTING = config()

def msg(info,level='info',wlog=True):
    def log(data,level='info'):
        import logging
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=SETTING.get('global',{}).get('log',None),
                    filemode='w')
        L = {
            'info':logging.info,
            'warning':logging.warning,
            'error':logging.error,
        }
        L.get(level,logging.info)(data)
    if wlog:
        log(info,level)
        
    code = {
        'info':0,'warning':1,'error':2
    }
    cCode = {
        'info':'\033[0;32m',
        'warning':'\033[0;33m',
        'error':'\033[0;31m',
    }
    title = 'Time: %s    Level: %s    code: %s'
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(cCode[level]+title % (now,level,code.get(level,0))+'\033[0m')
    print('\033[1mMessage\033[0m: '+info)
    if level == 'error':
        sys.exit(2)

class Display():
    def __init__(self,color='green',text='Loading...'):
        self.last = -1
        self.text = text
        color_choice = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'purple': '\033[35m',
            'gray': '\033[37m'
        }
        self.color = color_choice.get(color,'\033[32m')
        
    def output(self,d,f):
        num = int(round(d/float(f)*100))
        if num == self.last:
            return None
        if num == 0:
            sys.stdout.write("\033[?25l")
        if num == 100:
            sys.stderr.write(self.color+self.text+str(num)+'%\033[0m\n')
            sys.stdout.write("\033[?25h")
        sys.stderr.write(self.color+self.text+str(num)+'%\033[0m\r')
        self.last = num

def selectHashMethod(method='sha256'):
        support_method = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512,
        }
        sha = support_method.get(method,None)
        if not sha:
            class HashTypeError(Exception):
                pass
            raise HashTypeError('%s: Not found!' % method)
        return sha

def hashRandom(method='sha256'):
    sha = selectHashMethod(method)()
    sha.update(str(rand.random()))
    return sha.hexdigest()

def cov(num):
    num = int(num)
    if num > 1048576:
        return '%.3f MB' % (num/1048576.0)
    if num > 1024:
        return '%.3f KB' % (num/1024.0)
    else:
        return '%.3f B' % num
    
def startProject(target):
    def tar(src,dst):
        tmp = os.path.join('/tmp/',hashRandom('md5'))
        open(tmp,'wb').write(b64decode(src))
        tarf = tarfile.open(tmp)
        for i in tarf.getnames():
            tarf.extract(i,dst)
        os.remove(tmp)
    
    if os.path.exists(target):
        info = 'Project \033[1;34m%s\033[0m is really existed! Don\'t initialize repeat!' % target
        msg(info,'error')
    os.mkdir(target)
    os.mkdir(os.path.join(target,'build'))
    rootfsDir = os.path.join(target,'rootfs')
    tar(fsTree,rootfsDir)
    tar(busybox,os.path.join(rootfsDir,'bin'))
    
    config = '{\n    "tag":"",\n    "cmd":"",\n    "comment":"",\n    "created_by":"",\n    "docker_version":""\n}'
    open(os.path.join(target,'config.json'),'w').write(config)
    msg('Create Project \033[1;34m%s\033[0m success! Please into it' % target)

def dependent(execFile):
    if not os.path.exists('rootfs'):
        msg('Directory: \033[31mrootfs\033[0m not found! Please into project path then try again!','error')
    def ldSearch(ld):
        if not os.path.exists('/etc/ld.so.cache'):
            os.popen('ldconfig').read()
        ld_cache_file = open('/etc/ld.so.cache','rb').read()
        data = ld_cache_file.split('\x00')
        try:
            ld_path = data[data.index(ld)+1]
        except:
            return None
        return ld_path
    
    needs = [
        'libresolv.so.2',
        'libnss_dns.so.2',
        'libnss_files.so.2',
        'libgcc_s.so.1',
    ]
    libPath = 'rootfs/lib/'
    lib64Path = 'rootfs/lib64/'
    for i in needs:
        soPath = ldSearch(i)
        if 'lib64' in soPath:
            copy(soPath,lib64Path)
            print(soPath+'\t\t'+lib64Path)
        else:
            copy(soPath,libPath)
            print(soPath+'\t\t'+libPath)
        
    output = os.popen('ldd %s' % execFile).readlines()
    for i in output:
        if 'ld-linux' in i or 'linux-vdso.so' in i:
            continue
        soPath = ldSearch(i.split()[0])
        if 'lib64' in soPath:
            copy(soPath,lib64Path)
            print(soPath+'\t\t'+lib64Path)
        else:
            copy(soPath,libPath)
            print(soPath+'\t\t'+libPath)
    copy('/lib64/ld-linux-x86-64.so.2',lib64Path)
    msg('Copy all dependent to rootfs done!')

def tarFile1(path,mode='w'):
    fileName = hashRandom('md5')
    try:
        tar = tarfile.open('/tmp/%s' % fileName,mode)
        os.chdir(path)
        for root,d,files in os.walk('.'):
            for f in files:
                fullPath = os.path.join(root,f).replace('./','')
                tar.add(fullPath)
        tar.close()
        del d
    except:
        return False
    os.chdir(PATH)
    return '/tmp/'+fileName
    
def tarFile(path,mode='-cf'):
    fileName = '/tmp/'+hashRandom('md5')
    if mode == 'w:gz':
        mode = '-zcf'
    os.popen('cd %s;tar %s %s .' % (path,mode,fileName))
    return fileName

def dockerTest(target):
    if not os.path.exists('rootfs'):
        msg('Directory: \033[31mrootfs\033[0m not found! Please into project path then try again!','error')
    tag = hashRandom('md5')
    os.popen('cd %s;tar -cf - *|docker import - %s' % (target,tag)).read()
    os.system('docker run -ti --rm %s sh' % tag)
    os.popen('docker rmi -f %s' % tag)

def fileHashCheck(fileName=None,method='sha256',debug=False,showTime=False):
    out = Display(color='blue')
    sha = selectHashMethod(method)()
    fileLen = float(getsize(fileName))
    if debug:
        print('\033[34mFilesize\033[0m: %s    \033[34mHash\033[0m: %s' % (cov(fileLen),method))
    now = time.time()
    with open(fileName,'rb') as fp:
        def readFile():
            data = fp.read(8192)
            while data:
                yield data
                data = fp.read(8192)
        for i in readFile():
            sha.update(i)
            if showTime:
                out.output(fp.tell(),fileLen)
    if showTime:
        print('\033[34mUsed time\033[0m: %s' % (time.time() - now))
    return sha.hexdigest()

def utcTime():
    return time.strftime('%Y-%m-%dT%H:%M:%S.000000000Z')

def buildImage():
    def configParse():
        try:
            cf = json.loads(open('config.json','r').read())
        except:
            msg('File: \033[31mconfig.json\033[0m not found! Please into project path then try again!','error')
        setting = {
                'path':cf.get('path','rootfs'),
                'comment':cf.get('comment',' '),
                'created':utcTime(),
                'created_by':cf.get('created_by',' '),
                'Cmd':cf.get('cmd'),
                'tag_name':cf.get('tag','None'),
                'docker_version':cf.get('docker_version','1.10.0')
            }
        return setting
    
    setting = configParse()
    def mkId(setting):
        layerId = hashRandom()
        imageId = hashRandom()
        fileName = tarFile(setting['path'])
        layerHash = fileHashCheck(fileName,debug=True,showTime=True)
        return (layerId,imageId,fileName,layerHash)
    
    layerId,imageId,fileName,layerHash = mkId(setting)
    
    def mkManifest(setting):
        manifestJson = '''[{"Config":"image_json.json","RepoTags":null,"Layers":["layer_id/layer.tar"]}]'''
        manifest = json.loads(manifestJson)
        manifest[0][u'Layers'] = [u'%s/layer.tar' % layerId ]
        manifest[0][u'Config'] = u'%s.json' % imageId
        manifest[0][u'RepoTags'] = [setting['tag_name']]
        return json.dumps(manifest)
    
    def mkLayerjson(setting):
        layer_json = '''{"id":"layer_id","comment":"","created":"",\
    "container_config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,\
    "Cmd":[""],"Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},\"docker_version":"",\
    "config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,\
    "Cmd":[""],"Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},"architecture":"amd64","os":"linux"}'''
        layer = json.loads(layer_json)
        layer[u'comment'] = setting['comment']
        layer[u'created'] = setting['created']
        layer[u'container_config'][u'Cmd'] = [setting['created_by']]
        layer[u'config'][u'Cmd'] = setting['Cmd'].split()
        layer[u'id'] = layerId
        layer[u'docker_version'] = setting['docker_version']
        return json.dumps(layer)
    
    def mkImagejson(setting):
        image_json = '''{"architecture":"amd64","comment":"",\
    "config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,"Cmd":[""],"Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},\
    "container_config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":null,"Cmd":[""],\
    "Image":"","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},"created":"","docker_version":"",\
    "history":[{"created":"","created_by":"","comment":""}],\
    "os":"linux","rootfs":{"type":"layers","diff_ids":["sha256:"]}}'''
        image = json.loads(image_json)
        image[u'comment'] = setting['comment']
        image[u'created'] = setting['created']
        image[u'container_config'][u'Cmd'] = [setting['created_by']]
        image[u'docker_version'] = setting['docker_version']
        image[u'rootfs'][u'diff_ids'] = ['sha256:'+layerHash]
        image[u'config'][u'Cmd'] = setting['Cmd'].split()
        image[u'history'][0][u'comment'] = setting['comment']
        image[u'history'][0][u'created_by'] = setting['created_by']
        image[u'history'][0][u'created'] = setting['created']
        return json.dumps(image)
    
    def mkTree(setting):
        dirName = os.path.join('build',hashRandom('md5'))
        os.mkdir(dirName)
        os.mkdir(os.path.join(dirName,layerId))
        open(os.path.join(dirName,'manifest.json'),'w').write(mkManifest(setting))
        open(os.path.join(dirName,imageId+'.json'),'w').write(mkImagejson(setting))
        open(os.path.join(dirName,layerId,'json'),'w').write(mkLayerjson(setting))
        open(os.path.join(dirName,layerId,'VERSION'),'w').write('1.0')
        move(fileName,os.path.join(dirName,layerId,'layer.tar'))
        return dirName
    
    def build(setting):
        dirName = mkTree(setting)
        imageName = setting['tag_name'].replace(':','_')+"-image"
        print('Build success! Compress it now, Please waiting...')
        move(tarFile(dirName,mode='w:gz'),os.path.join(PATH,imageName+'.tar.gz'))
        rmtree(os.path.join(PATH,dirName))
        msg('Compress success! File: \033[1m%s.tar.gz\033[0m' % imageName)
    
    build(setting)

class Register():
    def __init__(self,port=None,address=None,path=None,pid=None):
        if port == None:
            try:
                port = int(SETTING.get('register',{}).get('port',11190))
            except:
                port = 11190
        self.port = port
        if address == None:
            try:
                address = SETTING.get('register',{}).get('listen','0.0.0.0')
            except:
                address = '0.0.0.0'
        self.address = address
        if path == None:
            try:
                path = SETTING.get('register',{}).get('workdir','.')
                if not os.path.exists(path):
                    os.mkdir(path)
            except:
                path = '.'
        os.chdir(path)
        if pid == None:
            try:
                pid = SETTING.get('register',{}).get('pid','/var/run/mdrs.pid')
                open(pid,'w').write(str(os.getpid()))
            except:
                open('/var/run/mdrs.pid','w').write(str(os.getpid()))
        else:
            open(pid,'w').write(str(os.getpid()))
        self.pid = pid
    
    def handler(self,conn,addr):
        '''
        header: {'method':'pull',file:'filename',size:10240,regex:'.*'}
                method: pull | push | search | stop | delete
        '''
        try:
            raw_header = conn.recv(1024)
            header = json.loads(raw_header)
        except:
            msg('Header parse failed! Header: %s' % raw_header,level='warning')
            conn.close()
            return None
        
        def readFile(fn, size=8192, method='rb'):
            class methodError(Exception):
                pass
            if method != 'r' and method != 'rb':
                raise methodError('Only \'rb\' or \'r\' method')
            with open(fn,method) as fp:
                data = fp.read(size)
                while data:
                    yield data
                    data = fp.read(size)
        
        def stop():
            time.sleep(0.1)
            os.kill(os.getpid(),2)
        
        def delete(fName):
            if os.path.exists(fName):
                os.remove(fName)
                conn.send('ok')
                msg('Delete image: %s Success!' % fName)
            else:
                conn.send('no')
                msg('Delete image: %s Failed!' % fName,'warning')
        
        
        def pull(fName):
            try:
                conn.send(json.dumps({"size":getsize(fName)}))
                code = conn.recv(10)
                if code.strip() == 'ok':
                    for i in readFile(fName):
                        conn.send(i)
                    msg('Client: %s:%s send success! Header:%s' % (addr[0],addr[1],raw_header))
                else:
                    msg("Get %s, send cancel" % code,'warning')
            except Exception:
                conn.send('no')
                msg('Client: %s:%s Error! Header: %s' % (addr[0],addr[1],raw_header),'warning')
                
        def push(fName):
            try:
                if os.path.exists(fName):
                    conn.send('no')
                    msg('File: %s already exists!' % fName)
                else:
                    conn.send('ok')
                    fp = open(fName,'wb')
                    while True:
                        data = conn.recv(8192)
                        if not data:
                            break
                        else:
                            fp.write(data)
                    fp.close()
                    if not getsize(fName):
                        msg('Client: %s:%s File: %s receive failed! Header: %s' % (addr[0],addr[1],fName,raw_header),'warning')
                        os.remove(fName)
                    else:
                        msg('Client: %s:%s File: %s receive success! Header: %s' % (addr[0],addr[1],fName,raw_header))
            except Exception:
                msg('Client: %s:%s Error! Header: %s' % (addr[0],addr[1],raw_header),level='warning')
            
        def search(regex):
            from re import findall
            result = []
            try:
                for i in os.listdir('.'):
                    if findall(regex,i):
                        result.append((i,getsize(i)))
                conn.send(json.dumps(result))
                msg('Client: %s:%s search success! Header: %s' % (addr[0],addr[1],raw_header))
            except Exception:
                msg('Search require Error! Header: %s' % raw_header,'warning')
        
        try:
            if header['method'] == 'pull':
                pull(header['filename'])
            elif header['method'] == 'push':
                push(header['filename'])
            elif header['method'] == 'search':
                search(header['regex'])
            elif header['method'] == 'stop':
                stop()
            elif header['method'] == 'delete':
                delete(header['filename'])
        finally:
            conn.close()
            
    def start(self):
        import threading
        def userExit():
            if os.path.exists(self.pid):
                os.remove(self.pid)
            msg('Stop server by user',level='warning')
            sys.exit(1)
        
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.address,self.port))
            s.listen(5)
            msg('OK! Server listen on: %s:%s' % (self.address,self.port))
            while True:
                try:
                    conn,addr = s.accept()
                except:
                    userExit()
                msg('Client %s:%s connect success!' % addr)
                threading.Thread(target=self.handler,args=(conn,addr)).start()
        except Exception:
            msg('Start server failed!','warning')
        finally:
            s.close()

class Client():
    def __init__(self,server=None):
        '''
        server: http://127.0.0.1/docker/images/
        '''
        if server == None:
            try:
                server = SETTING.get('client',{}).get('server','mdrs://127.0.0.1:11190')
            except:
                server = 'mdrs://127.0.0.1:11190'
        self.protocol = server.split('://')[0]
        if self.protocol == 'http':
            self.url = server
        else:
            self.address = server.split('://')[1].split(':')[0]
            try:
                self.port = int(server.split('://')[1].split(':')[1])
            except IndexError:
                self.port = 11190
            self.conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                self.conn.connect((self.address,self.port))
            except:
                msg("Server: %s connect failed!" % server,'error')
            
    def delete(self,itag):
        if self.protocol == 'http':
            msg('Sorry! not support delete on HTTP','error')
        if '-image.tar.gz' in itag:
            fname = itag
        elif ':' not in itag:
            itag = itag+':latest' 
            fname = itag.replace(':','_')+'-image.tar.gz'
        else:
            fname = itag.replace(':','_')+'-image.tar.gz'
            
        self.conn.send(json.dumps({"method":"delete","filename":fname}))
        response = self.conn.recv(20)
        if response == 'ok':
            msg('Delete image: %s Success! From register' % itag)
        else:
            msg('Delete image: %s Failed! From register' % itag,'error')
            
    def pull(self,itag):
        if '-image.tar.gz' in itag:
            fname = itag
        elif ':' not in itag:
            itag = itag+':latest' 
            fname = itag.replace(':','_')+'-image.tar.gz'
        else:
            fname = itag.replace(':','_')+'-image.tar.gz'
            
        tmpfile =  open(mktemp(),'w+b')
        if self.protocol == 'http':
            import urllib2
            if self.url[-1] == '/':
                url = self.url+fname
            else:
                url = self.url+'/'+fname
            msg('Download %s from %s' % (itag,url))
            try:
                tmpfile.write(urllib2.urlopen(url,timeout=2).read())
                msg('Download success!')
            except:
                msg('Pull error! Please check HTTP server or URL','error')
        else:
            self.conn.send(json.dumps({'method':'pull','filename':fname}))
            response = self.conn.recv(20)
            
            if response == 'no':
                msg('Pull error! Please try search it first!','error')
                
            msg('File size: %s download...' % json.loads(response)['size'])
            self.conn.send('ok')
            
            while True:
                data = self.conn.recv(8192)
                if data:
                    tmpfile.write(data)
                else:
                    msg('Download success!')
                    break
            self.conn.close()
            
        tmpfile.seek(0)    
        subprocess.Popen(['docker','load'],stdin=tmpfile).wait()
        msg('Import to docker success!')
        tmpfile.close()
        os.remove(tmpfile.name)
        
    def push(self,itag):
        if self.protocol == 'http':
            msg('Sorry! not support push on HTTP','error')
        def readFile(fp):
            data = fp.read(8192)
            while data:
                yield data
                data = fp.read(8192)
        
        if '-image.tar.gz' in itag:
            fname = itag.split('/')[-1]
            if os.path.exists(itag):
                fp = open(itag,'rb')
            else:
                msg('Push Error! File: %s not found!' % itag)
        else:
            msg("Save image from docker, Please waiting...")
            dok = subprocess.Popen(['docker','save',itag],stdout=subprocess.PIPE)
            fp = dok.stdout
            fname = itag.replace(':','_')+'-image.tar.gz'
        self.conn.send(json.dumps({'method':'push','filename':fname}))
        response = self.conn.recv(20)
        if response == 'no':
            msg('Push Failed! From register\'s info','error')
        if response == 'ok':
            msg('Save success! Push begin...')
            count = 0
            for i in readFile(fp):
                self.conn.send(i)
                count += 1
            self.conn.close()
        if count == 0:
            msg('Push Failed! From local\'s info','error')
        else:
            msg('Push success! File: %s' % fname)
           
    def search(self,regex='.*'):
        if regex == '*':
            regex = ".*"
        
        if self.protocol == 'http':
            import re,urllib2
            try:
                data = '\n'.join(re.findall(r'<a.*?gz</a>.*\d+',urllib2.urlopen(self.url).read()))
            except:
                msg('Pull error! Please check HTTP server or URL','error')
            result = []
            for i in re.findall(r'.*%s.*' % regex,data):
                if not i:
                    continue
                image = re.findall(r'href="(.*?)"',i)[0]
                size = i.split()[-1]
                result.append([image,size])
        else:
            self.conn.send(json.dumps({'method':'search','regex':regex}))
            result = json.loads(self.conn.recv(99999))
            
        for i in result:
            if 'index.html' in i:
                continue
            image = i[0].split('_')[0]
            tag = i[0][:-13].split('_')[1]
            itag = image+":"+tag
            if len(itag) < 10:
                itag = itag+(10-len(itag))*' '
            print('\033[34mImage\033[0m: %s\t\t\033[34mSize\033[0m: %s' % (itag,cov(i[1])))
        
    def stop(self):
        if self.protocol == 'http':
            msg('Sorry! not support stop on HTTP','error')
        self.conn.send('{"method":"stop"}')
        msg("Send stop signal to server success!")
    
def httpIndex(path=None):
    if path == None:
        path = SETTING.get('register',{}).get('workdir','.')
        
    template = '<a href="{image}">{image}</a>   {size}\r\n'
    index = os.path.join(path,'index.html')
    
    if os.path.exists(index):
        os.remove(index)
        
    images = os.listdir(path)
    with open(index,'w') as fp:
        for i in images:
            fp.write(template.format(image=i,size=getsize(os.path.join(path,i))))  
        msg('Create %s success!' % index)


def main():
    def usage():
        text = '''\033[1mUsage\033[0m: %s [OPTION] [TARGET]
        
        -h, --hele                  Display this help and exit
        -d, --depend                Search executable file dependent library
        -c, --create                Create new project and exit
        -t, --test                  Import project to docker and run it
        -b, --build                 Build docker image
        --pull                      Pull image from server
        --push                      Push image to server (only register)
        --stop                      Stop remote server (only register)
        --delete                    Delete image from server (only register)
        --html                      Create index.html (only HTTP)
        --server                    Start docker register server
        '''
        print(text)
    try:
        opts,args = getopt.getopt(sys.argv[1:],'d:tc:hb',
                                  ["build","depend=","help",
                                  "create=","test","pull=","push=",
                                  "stop","delete=","html","server",
                                  "search="]
                                  )
        del args
    except:
        usage()
        sys.exit(1)
    if len(opts) != 1:
        usage()
        sys.exit()
    if opts[0][0] in ['-c','--create']:
        startProject(opts[0][1])
    if opts[0][0] in ['-d','--depend']:
        dependent(opts[0][1])
    if opts[0][0] in ['-h','--help']:
        usage()
    if opts[0][0] in ['-t','--test']:
        dockerTest('rootfs')
    if opts[0][0] in ['-b','--build']:
        buildImage()
    if opts[0][0] == "--pull":
        Client().pull(opts[0][1])
    if opts[0][0] == "--push":
        Client().push(opts[0][1])
    if opts[0][0] == "--search":
        Client().search(opts[0][1])
    if opts[0][0] == "--delete":
        Client().delete(opts[0][1])
    if opts[0][0] == "--stop":
        Client().stop()
    if opts[0][0] == "--html":
        httpIndex()
    if opts[0][0] == "--server":
        Register().start()
    
if __name__ == '__main__':
    main()
