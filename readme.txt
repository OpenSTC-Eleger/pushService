# -*- coding: utf-8 -*-

    Copyright (C) 2012 SICLIC http://siclic.fr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>


1. Python packages Dependancies
	Pyro4
	
2. How to start

You'll have first to launch the daemon python script, then you'll be able to call internal URI (i.e. "PYRONAME:pushService")
to get an instance of PushService class. Then, use PushService#push(customer_dbname) to perform push of .txt files of the customer to its remote server

2.1 NameServer using Pyro4

First of all, you have to launch in a 1st shell:
python -m Pyro4.naming

This will simulate NameServer (to be able to use friendly URI on internal calls)

2.2 launch Daemon

Then, launch in a 2nd shell: 
python pushService.py

This will launch the daemon and initialize the http client (listenning on localhost).

2.3 Call URI to perform push of files

from you're client, call the URI : PYRONAME:pushService with a Pyro Proxy
It returns a PushService instance, then, use push() method, you only have to supply customer_dbname as parameter.

example of python client use : 
client = Pyro4.Proxy('PYRONAME:PushService')
client.push('siclic') #will push all existing files for 'siclic' for siclic customer to its remote server (must match a repository/siclic/ directory name)

3. Configuration

3.1 Logging

config.yml store the config of logging python object used in the script

3.2 Customers

customers.yml store the config of each customer : 
* username (remote user used for scp transactions)
* server: (remote url server to push files)
* path: (remote path to where push the files, usually a custom directory used by a Tiers software on the remote server)
Each key of the YAML files must match one of sub-directories of repository dir.
