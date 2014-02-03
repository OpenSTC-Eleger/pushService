# -*- coding: utf-8 -*-
import subprocess
import yaml
from yaml.error import YAMLError
import sys
import logging
from logging.config import dictConfig
import os
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer 
import shutil

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
            #initialize paths according to customers.yml
            host = customer.get('host','')
            username = customer.get('username','')
            path = customer.get('path','')
            base_path = '%s/%s' % ('repositories',db)
            local_path = '%s/todo' % (base_path,)
            files = ['%s/%s' % (local_path,f) for f in os.listdir(local_path)]
            #build shell command as string
            cmd = ' '.join(['scp','-v',' '.join(files), '%s@%s:%s' % (username,host,path)])
            myLogger.info('Trying to export files for "%s"' % db)
            myLogger.debug('Execute command : "%s"' % cmd)
            #process the cmd into shell context
            process = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            if process.wait() != 0:
                myLogger.error(process.communicate()[1])
                self.send_error(500, message="Internal error when sending files by ssh")
            else:
                myLogger.info("Success")
                self.send_response(200)
        else:
            myLogger.error('Error, not any customer config found for "%s"' % db)
            self.send_error(404, message='Not any customer repository found for "%s"' % db)

#first, initialize logging configuration
logging_config_file = open(logging_config_path, 'r')
dictConfig(yaml.load(logging_config_file))
myLogger = logging.getLogger()
myLogger.info('*****Initialize PushService daemon*****')

#then, initialize HTTP server
config = yaml.load(open(config_path, 'r'))
server = HTTPServer((config.get('servername',''),config.get('port','')), PushServiceHandler)

#and initialize customer configuration
myLogger.debug('*****Parsing customer file*****')
customer_file = open(customer_file_path)
customer_config = yaml.load(customer_file)

#I write PID on the .pid file to be usable as service
pidfile = open('/var/run/pushService.pid', 'w')
pidfile.write(str(os.getpid()))
pidfile.close()
myLogger.info('*****Launching PushService daemon*****')
server.serve_forever()