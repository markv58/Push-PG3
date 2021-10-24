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
                        "token": self.parent.api_key,
                        "user": self.parent.user_key,
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
