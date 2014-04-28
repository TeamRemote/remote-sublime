from . import diff_match_patch
import socket 
import sublime, sublime_plugin
import sys
import threading

get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

def create_server(port):
    host = '' 
    # port = 12345
    backlog = 1
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
    print(s)
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
    s.send(b'')    
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
            self.server = create_server(50000) #Server2 on 50000
            print("Creating client")
            self.client = create_client(12345) #Client2 to connect to server on 12345
           
    def run(self):
        print("In the run method")
        initConn = False
        while True:
            client, address = self.server.accept()
            print(client, address)
            if self.client is None:
                self.client = create_client(50000)
                print("Created client on host")
                if self.host: #If it is host send over the shadow to the joiner
                    print("Trying to send shadow: ", self.shadow)
                    client.send(self.shadow.encode(encoding="utf-8"))
                    print("Finished sending shadow")
            data = client.recv(4096)
            print("OMG DATA",data)
            if data:
                data = data.decode("utf-8")
                print("Received :", data)
                # IF this is not host and we have not received shadow, recv shadow and set bool flag to true
                if self.recv_shadow is False:
                    print("Receiving shadow", self.shadow)
                    self.shadow = data
                    sublime.set_timeout(lambda: self.callback(data), 1)
                    self.recv_shadow = True 
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
            print("Sending diffs")
            self.client.send(dmp.patch_toText(patch).encode(encoding='UTF-8'))
        self.shadow = new_buffer

    def end_session(self):
        self.server.close()
        self.client.close()