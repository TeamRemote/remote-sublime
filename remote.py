import sublime, sublime_plugin
from . import Session
import socket
import sys

class DiffListener(sublime_plugin.EventListener):
    """Listens for modifications to the view and gets the diffs using 
    Operational Transformation"""

    def __init__(self):
        # watched_views is a sessions of which currently open views are bound to 
        # remote-collab sessions. This allows the  EventListener to check if
        # on_modified events happened to the views it cares about, or to other 
        # views which it doesn't care about.
        self.sessions = []

    def on_modified_async(self, view):
        """Listens for modifications to views which are part of a currently
        active remote session."""
        if self.sessions:
            for session in self.sessions:
                if session.view is view:
                    current_buffer = view.substr(sublime.Region(0, view.size())) 
                    session.send_diffs(current_buffer)  

    def on_close(self, view): 
        """Check to see if views I care about are closed, and if they are,
        drop them from my watched-views"""
        if view in sessions.keys():
            del sessions[view]      

class StartSessionCommand(sublime_plugin.TextCommand):
    """Command to start a new RemoteCollab session for the current view"""
    get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

    def __init__(self, *args, **kwargs):
        self.df = DiffListener()
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def run(self, edit):     
        # this will have to connect to the remote server (getting the address
        # from the settings file), wait for the server to generate the session,
        # and tell the user the access token. it'll then have to start watching
        # the urrent view synchronizing
        session = Session(self.view, None)
        df.sessions.append(session)
        #session.patch_listener()
            
class ConnectToSessionCommand(sublime_plugin.WindowCommand):
    """Command to connect to an external RemoteCollab session."""
    def __init__(self, *args, **kwargs):
        self.df = DiffListener()
        sublime_plugin.ApplicationCommand.__init__(self, *args, **kwargs)

    # this will have to connect to the remote server (configured in settings file),
    # send the session token, make a new view containing the contents of the remote
    # session, and then start listening for modifications to that view and synchronizing   
    def run(self):
        self.window.show_input_panel(
            'Session IP Address',
            '',
            self.on_done,
            self.on_change,
            self.on_cancel)

    def on_done(self, input):
        """Input panel handler - creates a new session connected to the given IP address. """
        session = Session(self.window.new_file(), input)
        df.sessions.append(session)
        #session.patch_listener()

class CloseSessionCommand(sublime_plugin.TextCommand):
    """Command to close a RemoteCollab session."""
    def __init__(self, *args, **kwargs):
        sublime_plugin.ApplicationCommand.__init__(self, *args, **kwargs)

    # this will have to connect to the remote server (configured in settings file),
    # send the session token, make a new view containing the contents of the remote
    # session, and then start listening for modifications to that view and synchronizing   
    def run(self):
        session = next((session for session in DiffListener.sessions if session.view is self.view), None)
        if session is not None:
            session.end_session()
