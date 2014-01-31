# -*- coding: utf-8 -*-
import subprocess
import yaml
from yaml.error import YAMLError
import sys
import logging
from logging.config import dictConfig
import os
import daemon
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer 
from daemon.pidlockfile import TimeoutPIDLockFile


config_path = './config.yml'
logging_config_path = './logging_config.yml'
customer_file_path = './customer.yml'
customer_config = {}

class PushServiceHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        path = self.path.split('/')
        if len(path) > 2:
            if 'push_service' == path[1]:
                self.push(path[2])
            else:
                self.send_error(404, 'resource "%s" not found' % path[1])
        else:
            self.send_error(400, message='You must provide at least one resource (push_service for example) and one target (siclic for example) separated by a slash')
    
    def push(self, db):
        myLogger.info('Received request : push .txt files for "%s"' % db)
        customer = customer_config.get(db, None)
        if customer:
            host = customer.get('host','')
            username = customer.get('username','')
            path = customer.get('path','')
            local_path = '%s/%s/*.txt' % ('~/repositories',db)
            cmd = ' '.join(['scp','-v',local_path, '%s@%s:%s' % (username,host,path)])
            myLogger.info('Trying to export files for "%s"' % db)
            myLogger.debug('Execute command : "%s"' % cmd)
            process = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            if process.wait() != 0:
                myLogger.error(process.communicate()[1])
                self.send_error(500, message="Internal error when sending files by ssh")
            else:
                myLogger.info("Success")
                self.send_response(200)
        else:
            myLogger.error('Error, not any customer config found for "%s"' % db)
            self.send_error(404, message='Not any customer found for "%s"' % db)
#try:
#first, initialize logging configuration
logging_config_file = open(logging_config_path, 'r')
dictConfig(yaml.load(logging_config_file))
myLogger = logging.getLogger()
myLogger.info('*****Initialize PushService daemon*****')

#then, initialize HTTP server
config = yaml.load(open(config_path, 'r'))
server = HTTPServer((config.get('servername',''),config.get('port','')), PushServiceHandler)
#and initialize customer configuration
myLogger.debug('Parsing customer file')
customer_file_path = open(customer_file_path)
customer_config = yaml.load(customer_file_path)

pidfile = open('/var/run/pushService.pid', 'w')
pidfile.write(str(os.getpid()))
pidfile.close()
myLogger.info('*****Launching PushService daemon*****')
server.serve_forever()
