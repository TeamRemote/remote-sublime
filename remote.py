import sublime, sublime_plugin

class DiffListener(sublime_plugin.EventListener):
    """Listens for modifications to the view and gets the diffs using Operational Transformation"""

    def __init___(self):
        self.buffer = None
        self.last_buffer = None
        self.listening = False

    def on_modified_async(self, view):
        """Listens for modifications to the view."""
        if (listening):
            self.buffer = view.substr(sublime.Region(0, view.size()))# get the body text of the whole buffer
            send_deltas(diff(self.last_buffer, self.buffer))         # send the deltas to the server
            self.last_buffer = self.buffer                           # set the last buffer equal to the current buffer

    def diff(old, new):
        """Uses Operational Transformation to diff the new view against the old view."""
        # insert OT here

class StartSessionCommand(sublime_plugin.TextCommand):
    """Command to start a new RemoteCollab session for the current view"""
        def run():
            # this will have to connect to the remote server (getting the address
            # from the settings file), wait for the server to generate the session,
            # and tell the user the access token. it'll then have to start watching the
            # current view synchronizing

class ConnectToSessionCommand(sublime_plugin.ApplicationCommand):
    """Command to connect to an external RemoteCollab session."""
    # this will have to connect to the remote server (configured in settings file),
    # send the session token, make a new view containing the contents of the remote
    # session, and then start listening for modifications to that view and synchronizing

class ServerConnection:
    def __init__(self):
        # add constructor

    def send_deltas(diff):
        """Sends deltas to the server over the current connection."""
        # send the deltas over the current server connection

    # insert some kind of way to listen for deltas here? not sure how to synchronize...