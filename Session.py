import diff_match_patch
import socket 
import sublime, sublime_plugin
import sys

class Session: 
    
    get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

    def create_server():
    	host = '' 
    	port = 50000 
    	backlog = 5 
    	size = 4096 	
    	try: 
    	    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    	    s.bind((host,port)) 
    	    s.listen(backlog) 
    	except socket.error, (value,message): 
    	    if s: 
    	        s.close() 
    	    print "Could not open socket: " + message 
    	    sys.exit(1) 

    def get_remote_client(server):
    	client_connected = false
    	client_socket = None
    	size = 4096
    	while not client_connected:
    	    client_socket, address = server.accept()
    	    client_connected = true
    	    client_socket.send("Connected")
    	return client_socket

    def create_client(host):
    	host = 'localhost' 
    	port = 50000 
    	size = 4096 
    	s = None 
    	try: 
    	    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    	    s.connect((host,port)) 
    	except socket.error, (value,message): 
    	    if s: 
    	        s.close() 
    	    print "Could not open socket: " + message 
    	    sys.exit(1) 
    	return s	

    def __init__(self, view, is_creator):
        self.view = view
        self.shadow = get_buffer(self.view)
        self.server = None
        self.client = None
        self.dmp = diff_match_patch.diff_match_patch()
        dmp.Diff_Timeout = 0
        if is_creator:
        	self.server = create_server()
        	self.client = get_remote_client()
        else:
        	self.client = create_client('')
        	self.server = create_server()

    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
	    diffs = dmp.diff_main(self.shadow, new_buffer)
	    patch = dmp.patch_make(shadow, diffs)
 		self.client.send(dmp.patch_toText(patch))
        self.shadow = new_buffer

    def patch_listener(self, server):
    	while True: 
    	    client, address = s.accept() 
    	    data = client.recv(size) 
    	    if data:
    	    	# Check checksum etc.
    	        patch = dmp.patch_fromText(data) 
    	        self.shadow, shadow_results = dmp.patch_apply(patch, self.shadow)
    			get_buffer(self.view), view_results = dmp.patch_apply(patch, get_buffer(self.view)) 
    
  	def end_session(self):
  		self.server.close()
  		self.client.close()