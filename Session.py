import socket 
import diff_match_patch
import timeit 
import sys

class Session:
    
    def __init__(self, session_id, last_buffer, is_creator):
        self.session_id = session_id
        self.shadow = last_buffer
        self.server = None
        self.client = None
        if is_creator:
        	self.server = create_server()
        	self.client = get_remote_client()
        else:
        	self.client = create_client('')
        	self.server = create_server()

    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diff = diff(self.last_buffer, new_buffer)
        
        self.shadow = new_buffer

    def listen_for_patch(self, server):
    	# TODO: 

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
