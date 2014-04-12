# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2012 SICLIC http://siclic.fr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################
import subprocess
import yaml
from yaml.error import YAMLError
import sys
import logging
from logging.config import dictConfig
import os
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer 
import shutil

script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = '{}/config/config.yml'.format(script_dir)
logging_config_path = '{}/config/logging_config.yml'.format(script_dir)

class PushServiceHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split('/')
        if len(path) > 2:
            if 'push_service' == path[1]:
                self.push(path[2])
            elif 'create_customer' == path[1]:
                self.create(path[2])
            else:
                self.send_error(404, 'resource "{}" not found'.format(path[1]))
        else:
            self.send_error(400, message='You must provide at least one resource (ex: push_service, create_customer) and one target (siclic for example) separated by a slash')
    
    def create(self, name):
        myLogger.info('Creating new customer "{}"'.format(name))
        cust_dir = '{path}/{name}'.format(path=customer_conf_dir,name=name)
        try:
            if not os.path.isdir(cust_dir):
                os.makedirs('{}/todo'.format(cust_dir), 0750)
                os.makedirs('{}/archive'.format(cust_dir), 0750)
            else:
                myLogger.info('Customer directory "{}" already exists'.format(name))
                self.send_error(400, 'Customer "{}" already exists'.format(name))
        except:
            myLogger.info('Failed creating customer "{}" !!!'.format(name))
            self.send_error(400, 'Could not create customer "{}"'.format(name))

    def push(self, db):
        myLogger.info('Received request : push .txt files for "{}"'.format(db))
        customer_conf = '{confdir}/{name}.yml'.format(confdir=customer_conf_dir,name=db)
        customer_key = '{confdir}/{name}'.format(confdir=customer_keys_dir,name=db)
        if not os.path.isfile(customer_conf):
            self.send_error(404, 'Could not find customer YAML config file "{}"'.format(customer_conf))
        if not os.path.isfile(customer_key):
            self.send_error(404, 'Could not load customer SSH key "{}"'.format(customer_key))
        myLogger.info('Fetching config from {}'.format(customer_conf))
        customer = yaml.load(open(customer_conf, 'r'))
        if customer:
            #initialize paths according to customers.yml
            host = customer.get('host','')
            username = customer.get('username','')
            path = customer.get('path','')
            base_path = '{repo_dir}/{name}'.format(repo_dir=customer_repo_dir,name=db)
            local_path = '{}/todo'.format(base_path)
            files = ['{path}/{f}'.format(path=local_path,f=f) for f in os.listdir(local_path)]
            #build shell command as string
            cmd = ' '.join(['scp','-v','-i',customer_key,' '.join(files), '{user}@{host}:{path}'.format(user=username,host=host,path=path)])
            myLogger.info('Trying to export files for "{}"'.format(db))
            myLogger.debug('Execute command : "{}"'.format(cmd))
            #process the cmd into shell context
            process = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            if process.wait() != 0:
                myLogger.error(process.communicate()[1])
                self.send_error(500, message="Internal error when sending files by ssh")
            else:
                myLogger.info("Success")
                self.send_response(200)
        else:
            myLogger.error('Error, not any customer config found for "{}"'.format(db))
            self.send_error(404, message='Not any customer repository found for "{}"'.format(db))

#first, initialize logging configuration
dictConfig(yaml.load(open(logging_config_path, 'r')))
myLogger = logging.getLogger()

#and initialize customer configuration
myLogger.info('*****Loading config*****')
config = yaml.load(open(config_path, 'r'))
customer_conf_dir = config.get('customer-conf-dir','{}/customers/config'.format(script_dir))
customer_keys_dir = config.get('customer-keys-dir','{}/customers/keys'.format(script_dir))
customer_repo_dir = config.get('customer-repo-dir','{}/customers/repositories'.format(script_dir))
for cust_dir in [customer_conf_dir, customer_keys_dir, customer_repo_dir]:
    if not os.path.isdir(cust_dir): os.makedirs(cust_dir, 0755)

#then, initialize HTTP server
myLogger.info('*****Initializing PushService daemon*****')
server = HTTPServer((config.get('bind-address',''),config.get('port','')), PushServiceHandler)

#I write PID on the .pid file to be usable as service
pidfile = open('{}/run/pushService.pid'.format(script_dir), 'w')
pidfile.write(str(os.getpid()))
pidfile.close()
myLogger.info('*****Launching PushService daemon*****')
server.serve_forever()
