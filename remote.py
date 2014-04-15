import sublime, sublime_plugin

def diff(old, new):
    """Uses Operational Transformation to diff the new view 
    against the old view."""
    # insert OT here

class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.last_buffer = None

    def send_deltas(self, new_buffer):
        """Sends deltas to the server over the current connection 
        and sets the passed buffer as this view's buffer."""
        diff = diff(self.last_buffer, new_buffer)
        # TODO: insert code to actually send deltas here.
        self.last_buffer = new_buffer


class DiffListener(sublime_plugin.EventListener):
    """Listens for modifications to the view and gets the diffs
    using Operational Transformation"""

    def __init___(self):
        # watched_views is a dict of which currently open views are bound to 
        # remote-collab sessions. This allows the  EventListener to check if
        # on_modified events happened to the views it cares about, or to other 
        # views which it doesn't care about.
        self.watched_views = {}

    def on_modified_async(self, view):
        """Listens for modifications to ."""
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
        def run(self):     
            # this will have to connect to the remote server (getting the address
            # from the settings file), wait for the server to generate the session,
            # and tell the user the access token. it'll then have to start watching the
            # current view synchronizing

class ConnectToSessionCommand(sublime_plugin.ApplicationCommand):
    """Command to connect to an external RemoteCollab session."""
    # this will have to connect to the remote server (configured in settings file),
    # send the session token, make a new view containing the contents of the remote
    # session, and then start listening for modifications to that view and synchronizing
