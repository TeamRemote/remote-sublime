from . import Session
import sublime, sublime_plugin
import socket
import sys
import threading

class DiffListener(sublime_plugin.EventListener):
    """Listens for modifications to the view and gets the diffs using 
    Operational Transformation"""

    def __init__(self):
        # watched_views is a sessions of which currently open views are bound to 
        # remote-collab sessions. This allows the  EventListener to check if
        # on_modified events happened to the views it cares about, or to other 
        # views which it doesn't care about.
        self.session = None

    def on_modified_async(self, view):
        """Listens for modifications to views which are part of a currently
        active remote session."""
        if self.session is not None:
            if self.session.view is view:
                    current_buffer = view.substr(sublime.Region(0, view.size())) 
                    print("diff")
                    session.send_diffs(current_buffer)  

    def on_close(self, view): 
        """Check to see if views I care about are closed, and if they are,
        drop them from my watched-views"""
        if self.session is not None:
            if self.session.view is view:
                self.session.close()

class StartSessionCommand(sublime_plugin.TextCommand):
    """Command to start a new RemoteCollab session for the current view"""
    get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

    def run(self, edit):     
        DiffListener.session = Session.Session(self.view)
        print ("Started hosting session")
       
class ConnectToSessionCommand(sublime_plugin.WindowCommand):
    """Command to connect to an external RemoteCollab session."""

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

    def on_change(self, input):
        pass

    def on_cancel(self):
        pass
        
    def on_done(self, input):
        """Input panel handler - creates a new session connected to the given IP address. """
        
        DiffListener.session = Session.Session(self.window.new_file(), host=input)

#class CloseSessionCommand(sublime_plugin.TextCommand):
#    """Command to close a RemoteCollab session."""
#    def __init__(self, *args, **kwargs):
#        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)#

#    # this will have to connect to the remote server (configured in settings file),
#    # send the session token, make a new view containing the contents of the remote
#    # session, and then start listening for modifications to that view and synchronizing   
#    def run(self,edit):
#        session = next((session for session in df.sessions if session.view is self.view), None)
#        if session is not None:
#            session.end_session()


#class ReplaceViewCommand(sublime_plugin.TextCommand):
#    def run(self, edit, data):
#        self.view.replace(edit, sublime.Region(0, self.view.size()), data)