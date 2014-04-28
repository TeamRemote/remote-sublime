from . import diff_match_patch
import asyncore,socket 
import sublime, sublime_plugin
import sys

get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

#def create_server():
#    host = '' 
#    port = 4092
#    backlog = 5 
#    size = 4096     
#    try: 
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#        s.bind((host,port)) 
#        s.listen(backlog) 
#    except OSError as e: 
#        if s: 
#            s.close() 
#        print("Could not open socket: ", e)
#        sys.exit(1) 
#    return s

#def get_remote_client(server):
#    client_connected = False
#    client_socket = None
#    size = 4096
#    while not client_connected:
#        client_socket, address = server.accept()
#        client_connected = True
#        client_socket.send("Connected")
#    return client_socket

#def create_client(host):
#    print("help i'm trapped in a client factory")
#    port = 4092
#    size = 4096 
#    s = None 
#    try:
#        print("i'm trying!")
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#        s.connect((host,port)) 
#    except OSError as e: 
#        if s: 
#            s.close() 
#        print("Could not open socket: ", e) 
#        sys.exit(1)
#    else:
#        print("Unexpected error:", sys.exc_info()[0])
#    return s

class Server (asyncore.dispatcher_with_send):
    def __init__(self, host, port, parent):
        asyncore.dispatcher.__init__(self)
        self.parent = parent
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, 12345))
        self.listen(1)

    def handle_accepted(self, sock, addr):
        self.parent.address = addr
        PatchHandler(sock)

    def handle_connect(self):
        sock, addr = self.accept()
        sock.send(self.parent.shadow)

class PatchHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(4096)
        patch = self.parent.dmp.patch_fromText(data)
        self.parent.shadow, shadow_results = self.parent.dmp.patch_apply(patch, self.parent.shadow)
        current_buffer = self.parent.get_buffer(self.view)
        current_buffer, view_results = self.parent.dmp.patch_apply(patch, current_buffer)
        # Replace the view contents with the new buffer
        self.parent.view.replace(edit, sublime.Region(0, self.parent.view.size), current_buffer)

class Client(asyncore.dispatcher_with_send):
    def __init__(self, host, port, parent):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host,port))
        self.buffer = []

    def handle_close(self):
        self.close()

    def handle_write(self):
        sent = self.buffer.pop()
        self.send(sent)

    def handle_read(self):
        self.parent.shadow = self.recv(4096)    # ???

    def writable(self):
        return (len(self.buffer) > 0)
    
class Session: 
    
    def __init__(self, view, host):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        print("im session __init__")
        self.view = view
        self.shadow = get_buffer(self.view)
        self.server = None
        self.client = None
        self.address = None
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0
        if host is None:
            print ("i'm host")
            self.server = Server('', 12345, self)
            self.client = Client('localhost', 12345, self)
        else:
            print ("i'm not host?")
            self.client = Client(host, 12345, self)
            self.server = Server(host, 12345, self)
            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.client.buffer.append(self.dmp.patch_toText(patch))
        self.shadow = new_buffer

    def end_session(self):
        self.server.close()
        self.client.close()