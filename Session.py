from . import diff_match_patch
import socket 
import sublime
import sublime_plugin
import sys
import threading
get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

ENCODING = "utf_8"

class Transmitter(threading.Thread):
    """
    Sends diffs over a socket.
    """
    def __init__(self, socket, parent):
        super(Sender, self).__init__()
        self.socket = socket
        self.parent = parent
        self.queue = []

    def transmit(self, diff):
        self.queue.append(diff)

    def run(self):
        while True:
            if queue: 
                # Pop off the first item in the queue and encode it
                data = queue.pop().encode(ENCODING)
                # send the message over the socket
                self.socket.send(data)

class Reciever (threading.Thread):
    """
    Listens on a socket and patches the view with the recieved diffs.
    """
    def __init__(self, socket, parent):
        super(Reciever, self).__init__()
        self.socket = socket
        self.parent = parent

    def run(self):
        while True:
            data = self.socket.recv(4096)
            if data:
                data = data.decode(ENCODING)
                parent.patch_view(data)

class Session():
    
    def __init__(self, view, host, edit, is_host=False):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        self.host = host
        self.port = 12345 # This should be set from prefs file later
        self.view = view
        self.edit = edit
        self.shadow = get_buffer(self.view)
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host,self.port))
            self.socket.listen(1)
        except OSError as e:
            if self.socket:
                self.socket.close()
            print("Error opening socket: ", e)
        else: 
            conn, address = s.accept()
            print ("Connected to ", address)
            self.reciever = Reciever(conn, self)
            self.transmitter = Transmitter(conn, self)
            self.transmitter.run()
            self.reciever.run()
            if is_host:
                self.transmitter.transmit(get_buffer(self.view))
                print ("Sent initial buffer")
            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.transmitter.transmit(self.dmp.patch_toText(patch))
        self.shadow = new_buffer

    def patch_view (self, text):
        patch = self.dmp.patch_fromText(data)
        self.shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
        current_buffer = self.get_buffer(self.view)
        self.view.replace(edit, sublime.Region(0, self.view.size()), current_buffer)

    def close(self):
        self.socket.close()