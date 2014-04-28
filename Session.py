from . import diff_match_patch
import asyncore,socket 
import sublime, sublime_plugin
import sys

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
    except OSError as e: 
        if s: 
            s.close() 
        print("Could not open socket: ", e)
        sys.exit(1) 
    return s

def get_remote_client(server):
    client_connected = False
    client_socket = None
    size = 4096
    while not client_connected:
        client_socket, address = server.accept()
        client_connected = True
        client_socket.send("Connected")
    return client_socket

def create_client(host):
    port = 50000 
    size = 4096 
    s = None 
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((host,port)) 
    except OSError as e: 
        if s: 
            s.close() 
        print("Could not open socket: ", e) 
        sys.exit(1) 
    return s    
    
class Session: 
    
    def __init__(self, view, host):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        self.view = view
        self.shadow = get_buffer(self.view)
        self.server = None
        self.client = None
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0
        if not host:
            self.server = create_server()
            self.client = create_client('')
        else:
            self.client = create_client('')
            self.server = create_server()
            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.client.send(dmp.patch_toText(patch))
        self.shadow = new_buffer

    def patch_listener(self):
        size = 4096
        while True:
            client, address = self.server.accept()
            data = client.recv(size)
            if data:
                # Check checksum etc.
                patch = dmp.patch_fromText(data)
                self.shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
                current_buffer = get_buffer(self.view)
                current_buffer, view_results = self.dmp.patch_apply(patch, current_buffer)
                # Replace the view contents with the new buffer
                self.view.replace(edit, sublime.Region(0, self.view.size), current_buffer)

    def end_session(self):
        self.server.close()
        self.client.close()