#!/usr/bin/env python3

import udi_interface
import sys
import time
import subprocess
import http.client
import urllib
import requests

LOGGER = udi_interface.LOGGER
          
ACTION = ['-',
	  'On',
	  'Off',
	  'Light on',
	  'Light off',
	  'Open',
	  'Closed',
	  'Locked',
	  'Unlocked',
	  'Lock jammed',
	  'Motion detected',
	  'Water leak',
	  'Rang',
	  'At home',
	  'Away',
	  'Offline',
	  'Low battery',
	  'Armed',
	  'Disarmed',
	  'Triggered',
	  'Don''t forget!',
	  'WARNING',
	  'EMERGENCY',
	  'Heat warning',
	  'Cold warning',
	  'Reset'
         ] 

class Controller(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'Push'
        self.api_key = 'none'
        self.user_key = 'none'
        self.d_read = False
        	
        self.Parameters = Custom(polyglot, 'customparams')
        
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)
	
	
        polyglot.ready()
        polyglot.addNode(self)
        
    def parameterHandler(self, params):
        self.poly.Notices.clear()
        self.Parameters.load(params)

        if 'api_key' in params:
            self.api_key = params['api_key']               
        if 'user_key' in params:
            self.user_key = params['user_key']
        if 'disclaimer_read' in params:
            self.d_read = params['disclaimer_read']
        
        for key, val in params.items():
            _key = key.lower()
            if _key == 'api_key' or _key == 'user_key' or _key == 'disclaimer_read': # should parse out the keys, all others will be node
                pass
            else:
                _val = key.lower()
                _cleanaddress = _val.replace(' ','')
                _address = (_cleanaddress[:12] + _cleanaddress[-2:])
                _key = key
                self.poly.addNode(thingnode(self.poly, self.address, _address, _key))
		
        if self.api_key == '':
            self.poly.Notices['api'] = 'No api key, please enter your key.'                                                
        if self.user_key == '':
            self.poly.Notices['user'] = 'No user key, please enter your key.'

        if not self.d_read:
            self.poly.Notices['disc'] = 'Please read the Disclaimer <a target="_blank" href="https://github.com/markv58/UDI-Push/blob/master/Disclaimer.md">here</a> to remove this notice.'


    def start(self):
        LOGGER.info('Started Push Nodeserver')
        self.setDriver('ST', 1)
        LOGGER.info('If you have just upgraded hit the Update Profile button and restart the Admin Console')
        
    def query(self):
        for node in self.poly.nodes():
            node.reportDrivers()

    def delete(self):
        LOGGER.info('Deleting the Push Nodeserver.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    id = 'controller'

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]

    
class thingnode(udi_interface.Node):

    def __init__(self, controller, primary, address, name):
        super(thingnode, self).__init__(controller, primary, address, name)
        self.title = str(name)
        
    def send_pushover(self, command = None):
        _message = int(command.get('value'))
        try:
            LOGGER.info("Sending Pushover message %s %s", self.title, ACTION[_message])
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
                    urllib.parse.urlencode({
                        "token": self.primary.api_key,
                        "user": self.primary.user_key,
                        "title": self.title,
                        "message": ACTION[_message],
                    }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
            conn.close()
        except Exception as inst:
            LOGGER.error("Error sending to pushover: " + str(inst))

    id = 'thingnodetype'

    commands = {
                'ACTIONS': send_pushover
                }
 
    
if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        polyglot.updateProfile()
        polyglot.setCustomParamsDoc()
        Controller(polyglot, 'controller', 'controller', 'Push NodeServer')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
