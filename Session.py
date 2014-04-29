from . import diff_match_patch
import socket 
import sublime
import sublime_plugin
import sys
import threading
import time

get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

ENCODING = "utf_8"

def debug(message):
    t = time.localtime()
    print("[{thread}: {timestamp}] ".format(
        thread=threading.current_thread(), 
        timestamp = time.strftime('%H:%M:%S')
        ), message)


class Transmitter(threading.Thread):
    """
    Sends diffs over a socket.
    """
    def __init__(self, socket, parent):
        super(Transmitter, self).__init__()
        self.socket = socket
        self.parent = parent
        self.queue = []

    def transmit(self, diff):
        self.queue.append(diff)
        debug("transmitter enqueued {d}".format(d = diff))

    def run(self):
        while True:
            if self.queue: 
                # Pop off the first item in the queue and encode it
                data = self.queue.pop().encode(ENCODING)
                # send the message over the socket
                self.socket.send(data)
                debug("sent patch over socket {s}".format(s = self.socket))
                debug("queue: {q}".format(q = self.queue))

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
                debug ("recieved data: {d}".format(d = data))
                data = data.decode(ENCODING)
                self.parent.patch_view(data)

class Session(threading.Thread):
    
    def __init__(self, view, host=False):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        super(Session, self).__init__()
        self.port = 12345 # This should be set from prefs file later
        self.view = view
        self.shadow = get_buffer(self.view)
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0
        self.transmitter = None
        self.reciever = None
        self.socket = None
        self.host = host
        self.start()

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.host is False:
                sock.bind(('',self.port))
                sock.listen(1)
            else:
                sock.connect((self.host, 12345))
        except OSError as e:
            if sock:
                sock.close()
            print("Error opening socket: ", e)
        else:
            if self.host is False: 
                conn, address = sock.accept()
                print ("Accepted connection from ", address)
                self.reciever = Reciever(conn, self)
                self.transmitter = Transmitter(conn, self)
                self.transmitter.start()
                self.reciever.start()
                self.transmitter.transmit(get_buffer(self.view))
                print ("Sent initial buffer")
                self.socket = conn
            else:
                self.reciever = Reciever (sock, self)
                self.transmitter = Transmitter (sock, self)
                self.reciever.start()
                self.transmitter.start()
                self.socket = sock

            
    def send_diffs(self, new_buffer):
        """Sends deltas to the server over the current connection and sets the 
        passed buffer as this view's buffer."""
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        patch = self.dmp.patch_make(shadow, diffs)
        self.transmitter.transmit(self.dmp.patch_toText(patch))
        self.shadow = new_buffer

    def patch_view (self, data):
        patch = self.dmp.patch_fromText(data)
        self.shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
        current_buffer = self.get_buffer(self.view)
        self.view.replace(edit, sublime.Region(0, self.view.size()), current_buffer)

    def close(self):
        self.socket.close()
