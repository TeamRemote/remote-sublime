from . import diff_match_patch
import asyncore,socket 
import sublime, sublime_plugin
import sys
import threading
get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

class Server (asyncore.dispatcher_with_send):
    def __init__(self, port, parent):
        asyncore.dispatcher.__init__(self)
        self.parent = parent
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(1)

    def handle_accepted(self, sock, addr):
        self.parent.address = addr
        print(self.parent.address)
        print("Connected to", addr)
        PatchHandler(sock, self.parent)

    def handle_connect(self):
        print("In handling method")
        #sock, addr = self.accept()
        #print("sent shadow: ", self.parent.shadow)
        #sock.send(self.parent.shadow)

class PatchHandler(asyncore.dispatcher_with_send):
    def __init__(self, parent):
        asyncore.dispatcher.__init__(self)
        self.session = parent
    def handle_read(self):
        #Needs to handle stuff
        data = self.recv(4096)
        data = data.decode("utf-8")
        ###If the shadow is empty/ some bool flag/ it is not host
        ###...this should be the shadow not the patch....
        # else do normal patch stuff
        patch = self.parent.dmp.patch_fromText(data)
        self.parent.shadow, shadow_results = self.parent.dmp.patch_apply(patch, self.parent.shadow)
        current_buffer = self.parent.get_buffer(self.view)
        current_buffer, view_results = self.parent.dmp.patch_apply(patch, current_buffer)
        # Replace the view contents with the new buffer
        sublime.set_timeout(lambda: self.session.callback(current_buffer), 1)

class Client(asyncore.dispatcher_with_send):
    def __init__(self, port, parent):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Trying to connect to", host, port)
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
            self.server = create_server(12345, self) #Server1 on 12345
            #self.client = create_client(50000) #Client to connect to server o
        else:
            self.recv_shadow = False
            print("Creating server")
            self.server = create_server(50000, self) #Server2 on 50000
            print("Creating client")
            self.client = create_client(12345, self) #Client2 to connect to server on 12345        
            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.client.buffer.append(self.dmp.patch_toText(patch).encode(encoding='UTF-8'))
        self.shadow = new_buffer

    def callback(self, data):
        self.view.run_command("replace_view",{"data": data})

    def end_session(self):
        self.server.close()
        self.client.close()