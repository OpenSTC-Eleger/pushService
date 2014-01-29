# -*- coding: utf-8 -*-
import Pyro4
import subprocess
import yaml
from yaml.error import YAMLError
import sys
import logging
from logging.config import dictConfig
import os
config_path = './config.yml'
customer_file_path = './customer.yml'
#myLogger.setLevel('debug')
#myLogger.addHandler(logging.handlers.TimedRotatingFileHandler('logs/push-service-logs.log',when='d'))


class PushService(object):
    
    def __init__(self, customer_config):
        self.customer_config = customer_config
    
    def push(self, db):
        myLogger.info('Received request : push .txt files for "%s"' % db)
        customer = self.customer_config.get(db, None)
        if customer:
            host = customer.get('host','')
            username = customer.get('username','')
            path = customer.get('path','')
            local_path = '%s/%s/*.txt' % ('./repository',db)
            cmd = ' '.join(['scp',local_path, '%s@%s:%s' % (username,host,path)])
            myLogger.info('Trying to export files for "%s"' % db)
            myLogger.debug('Execute command : "%s"' % cmd)
            process = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            if process.wait() != 0:
                myLogger.error(process.communicate()[1])
            else:
                myLogger.info("Success")
                myLogger.debug(process.communicate()[0])
        else:
            myLogger.error('Error, not any customer config found for "%s"' % db)

try:
    #logging.info('-> Yes my Lord ?')
    #logging.debug('Parsing config file')
    config_file = open(config_path, 'r')
    dictConfig(yaml.load(config_file))
    myLogger = logging.getLogger()
    myLogger.info('*****Starting PushService daemon*****')
    myLogger.debug('Parsing customer file')
    customer_file_path = open(customer_file_path)
    pushService = PushService(yaml.load(customer_file_path))
except IOError:
    myLogger.error('could not open customer_file_path file, check if it is present')
    sys.exit(1)
except YAMLError:
    myLogger.error('error parsing customer_file_path file')
    sys.exit(1)
    
daemon = Pyro4.Daemon()
server = Pyro4.locateNS()
uri = daemon.register(pushService, "pushService")
server.register('pushService',uri)
daemon.requestLoop()