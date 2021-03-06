from . import diff_match_patch
from collections import deque
import socket
import sublime
import sublime_plugin
import sys
import threading
import time

ENCODING = "utf_8"

def debug(message, exception = None):
    """
    Helper function for printing debug messages with timestamps and thread names.
    """
    t = time.localtime()
    stamp = "[{thread}-{id} {timestamp}] ".format(
                                                thread = threading.current_thread().name,
                                                id = threading.get_ident(),
                                                timestamp = time.strftime('%H:%M:%S')
                                                )
    print(stamp, message)
    if exception: print (stamp, exception)


class Transmitter(threading.Thread):
    """
    Sends diffs over a socket.
    """
    def __init__(self, socket, parent):
        super(Transmitter, self).__init__()
        self.name = "({s}-{id}) Transmitter".format(
                                                    s = parent.name,
                                                    id = parent.ident,
                                                    )
        self.socket = socket
        self.parent = parent
        self.queue = deque([])

    def transmit(self, diff):
        """
        Function called by other threads to enqueue a diff in this transmitter's
        send buffer.
        """
        self.queue.append(diff)
        debug("transmitter enqueued {d}".format(d = diff))

    def run(self):
        debug ("started")
        while True:
            if self.queue:
                # Pop off the first item in the queue and encode it
                data = self.queue.popleft().encode(ENCODING)
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
        self.name = "({s}-{id}) Reciever".format(
                                                s = parent.name,
                                                id = parent.ident,
                                                )
        self.socket = socket
        self.parent = parent

    def run(self):
        debug ("started")
        while True:
            data = self.socket.recv(4096)
            if data: #If we've recieved data on our socket...
                debug ("recieved data: {d}".format(d = data))
                data = data.decode(ENCODING) # decode the patch
                self.parent.patch_view(data) # patch the session's view

class Session(threading.Thread):

    def __init__(self, view, host=None):
        """
        Constructor for a Session. Host is the IP address of the host we are connecting to.
        If we are the host, host should equal 'None'.
        """
        super(Session, self).__init__()
        self.name = "Host" if host is None else "Client"
        self.port = 12345 # This should be set from prefs file later
        self.view = view
        self.shadow = self.get_buffer()
        self.dmp = diff_match_patch.diff_match_patch()
        self.dmp.Diff_Timeout = 0
        self.transmitter = None
        self.reciever = None
        self.socket = None
        self.init_socket = None
        self.host = host
        self.start()

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.host is None: # if the remote host is None, we are the host.
                sock.bind(('',self.port))
                debug("bound socket, listening for remote")
                sock.listen(1)
            else:
                debug("connecting to {h}:{p}".format(h = self.host, p = self.port))
                sock.connect((self.host, self.port))
        except OSError as e:
            if sock:
                sock.close()
            debug("Error opening socket: ", e)
        else:
            if self.host is None: # If we are the host...
                conn, address = sock.accept()               # accept a connection from the remote
                debug ("Accepted connection from {a}".format (a = address))
                self.reciever = Reciever(conn, self)        # start a reciever for the remote
                self.transmitter = Transmitter(conn, self)  # start a transmitter for the remote
                self.transmitter.start()
                self.reciever.start()
                self.initial_patch()        # send the initial patch to the remote
                self.socket = conn          # our socket is the socket bound to the remote
                self.init_socket = sock     # keep a reference to the initial socket for cleanup
            else: # Otherwise, we're the remote
                self.reciever = Reciever (sock, self)       # start a reciever for the host
                self.transmitter = Transmitter (sock, self) # and a transmitter
                self.reciever.start()
                self.transmitter.start()
                self.socket = sock

    def initial_patch(self):
        """
        Sends the initial buffer contents to the remote. This is only called if we are the host.
        """
        diffs = self.dmp.diff_main('', self.shadow)
        patch = self.dmp.patch_make('', diffs)
        debug ("Made initial patch.")
        self.transmitter.transmit(self.dmp.patch_toText(patch))
        debug ("Sent initial patch to remote.")

    def send_diffs(self, new_buffer):
        """
        Sends diffs to the other peer over the current connection and sets the
        current buffer to the local shadow.
        """
        diffs = self.dmp.diff_main(self.shadow, new_buffer)
        debug ("Made diffs: {d}".format(d = diffs))
        patch = self.dmp.patch_make(self.shadow, diffs)
        debug ("Made patch: {p}".format(p = diffs))
        self.transmitter.transmit(self.dmp.patch_toText(patch))
        self.shadow = new_buffer

    def patch_view (self, data):
        """
        Patches this session's bound text buffer with a patch recieved from the remote peer.
        FIXME: thhis doesn't work correctly.
        """
        patch = self.dmp.patch_fromText(data)
        shadow, shadow_results = self.dmp.patch_apply(patch, self.shadow)
        if False in shadow_results:
            debug ("Patch application failed, buffer may be out of sync")
        else:
            self.shadow = shadow
            try:
                self.view.run_command("update_buffer", {"new_buffer": self.shadow})
            except Exception as e:
               debug ("Error occured while editing buffer ", e)

    def close(self):
        """
        Closes a session, releasing both the socket and the initial socket
        if they are available.
        """
        if self.socket is not None:
            debug ("Closing and shutting down socket {s}".format(self.socket))
            self.socket.shutdown()
            self.socket.close()
            debug ("Closed socket.")
        if self.init_socket is not None:
            debug ("Closing and shutting down handshake socket {s}".format(self.init_socket))
            self.socket.shutdown()
            self.init_socket.close()
            debug ("Closed socket.")

    def get_buffer(self):
        return self.view.substr(sublime.Region(0, self.view.size()))
