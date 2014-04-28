from . import diff_match_patch
import socket 
import sublime, sublime_plugin
import sys
import threading

get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

def get_remote_client(server):
    client_connected = False
    client_socket = None
    size = 4096
    while not client_connected:
        client_socket, address = server.accept()
        client_connected = True
        client_socket.send("Connected")
    return client_socket
def create_server(port):
    host = '' 
    # port = 12345
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
def create_client(port):
    host = 'localhost'
    # port = 50000 
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
    s.send(b'Init connection')    
    return s    
    
class Session(threading.Thread): 
    
    def __init__(self, view, host, edit):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        threading.Thread.__init__(self)
        self.view = view
        self.edit = edit
        self.shadow = get_buffer(self.view)
        self.server = None
        self.client = None
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0
        self.host = host
        if self.host:
            self.recv_shadow = True
            self.server = create_server(12345) #Server1 on 12345
            #self.client = create_client(50000) #Client to connect to server o
        else:
            self.recv_shadow = False
            print("Creating server")
            self.server = create_server(50000) #Client2 to connect to server on 12345
            print("Creating client")
            self.client = create_client(12345) #Server2 on 50000
            
    
    def run(self):
        print("In the run method")
        initConn = False
        while True:
            client, address = self.server.accept()
            if self.client is None:
                self.client = create_client(50000)
                if not self.host: #If it is not host send over the shadow
                    client.send(self.shadow)

            data = client.recv(4096)
            if data:
                data = data.decode("utf-8")
                # IF this is not host and we have not received shadow, recv shadow and set bool flag to true
                if not self.recv_shadow:
                    self.shadow = data
                    sublime.set_timeout(lambda: self.callback(data), 1)
                    self.recv_shadow = True 
                #Else if it is the host without an initial connection
                elif self.host and not initConn:
                    print(data)
                    initConn = True
                else:   
                    patch = dmp.patch_fromText(data)
                    self.shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
                    current_buffer = get_buffer(self.view)
                    current_buffer, view_results = self.dmp.patch_apply(patch, current_buffer)
                    # Replace the view contents with the new buffer
                    sublime.set_timeout(lambda: self.callback(current_buffer), 1)

    def callback(self, data):
        self.view.run_command("replace_view",{"data": data})

    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        if self.client is not None:
            self.client.send(dmp.patch_toText(patch).encode(encoding='UTF-8'))
        self.shadow = new_buffer

    # def patch_listener(self):
    #     while True:
    #         client, address = self.server.accept()
    #         if self.client is None:
    #             self.client = client
    #         data = client.recv(size)
    #         if data:
    #             # Check checksum etc.
    #             patch = dmp.patch_fromText(data)
    #             self.shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
    #             current_buffer = get_buffer(self.view)
    #             current_buffer, view_results = self.dmp.patch_apply(patch, current_buffer)
    #             # Replace the view contents with the new buffer

    #             self.view.replace(edit, sublime.Region(0, self.view.size), current_buffer)

    def end_session(self):
        self.server.close()
        self.client.close()