from . import diff_match_patch
import asyncore,socket 
import sublime, sublime_plugin
import sys
import threading
get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

class Session():
    
    def __init__(self, view, host, edit):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """  
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
            self.server = Server(12345, self) #Server1 on 12345
            #self.client = create_client(50000) #Client to connect to server o
        else:
            self.recv_shadow = False
            print("Creating server")
            self.server = Server(50000, self) #Server2 on 50000
            print("Creating client")
            self.client = Client(12345, self) #Client2 to connect to server on 12345        
            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.client.buffer.append(self.dmp.patch_toText(patch).encode(encoding='UTF-8'))
        self.shadow = new_buffer

    def callback(self, data):
        self.view.run_command("replace_view",{"data": data})

    def run(self):
        asyncore.loop()

    def end_session(self):
        self.server.close()
        self.client.close()