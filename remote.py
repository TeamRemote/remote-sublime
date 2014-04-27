import sublime, sublime_plugin
import Session
import socket
import sys

def diff(old, new):
    """Uses Operational Transformation to diff the new view against the old view."""
    # insert OT here

def create_server_socket():
   host = '' 
   port = 50000 
   backlog = 1 
   size = 1024 
   s = None 
   try: 
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
       s.bind((host,port)) 
       s.listen(backlog) 
   except socket.error, (value,message): 
       if s: 
           s.close() 
       print "Could not open socket: " + message 
       sys.exit(1) 
    return s

def create_client_socket(host):
    port = 50000 
    size = 1024 
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

def server_listener(socket):
    size = 4096
    while True:
        client, address = socket.accept()
        data = client.rec(size)


class DiffListener(sublime_plugin.EventListener):
    """Listens for modifications to the view and gets the diffs using 
    Operational Transformation"""

    def __init___(self):
        # watched_views is a dict of which currently open views are bound to 
        # remote-collab sessions. This allows the  EventListener to check if
        # on_modified events happened to the views it cares about, or to other 
        # views which it doesn't care about.
        self.watched_views = {}

    def on_modified_async(self, view):
        """Listens for modifications to views which are part of a currently
        active remote session."""
        if view in watched_views.keys():
            # get the body text of the whole buffer
            buff = view.substr(sublime.Region(0, view.size()))
            # send the deltas to the server
            watched_views[view].send_deltas(buff)   

    def on_close(self, view): 
        """Check to see if views I care about are closed, and if they are,
        drop them from my watched-views"""
        if view in watched_views.keys():
            del watched_views[view]      

class StartSessionCommand(sublime_plugin.TextCommand):
    """Command to start a new RemoteCollab session for the current view"""
    get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

        def run(self):     
            # this will have to connect to the remote server (getting the address
            # from the settings file), wait for the server to generate the session,
            # and tell the user the access token. it'll then have to start watching
            # the urrent view synchronizing
            #session_id = get_id_from_server()
            #DiffListener.watched_views[self.view] = Session(session_id, get_buffer(self.view))
            
            # Create a server socket and start listening for a client to connect
            server_socket = create_server_socket()
            client_connected = false
            client_socket = None
            size = 4096
            while not client_connected:
                client_socket, address = server_socket.accept()
                client_connected = true
                client_socket.send("Connected")
            
            while True:
                client, address = server_socket.accept()
                data = client.recv(size)
                if data:
                    #applypatch(data, get_buffer(self.view))
            
class ConnectToSessionCommand(sublime_plugin.ApplicationCommand):
    """Command to connect to an external RemoteCollab session."""
    # this will have to connect to the remote server (configured in settings file),
    # send the session token, make a new view containing the contents of the remote
    # session, and then start listening for modifications to that view and synchronizing
    
    def run(self):
        host = '' # This should be from the user?
        client_socket = create_client_socket('')
        client_socket.send("Initializing connection")
        server_socket = create_server_socket()
        
