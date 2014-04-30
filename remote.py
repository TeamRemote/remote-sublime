from . import Session
import sublime, sublime_plugin
import socket
import sys
import threading

session = None

class DiffListener(sublime_plugin.EventListener):
    """
    Listens for modifications to the view and gets the diffs using
    Operational Transformation
    """

    def on_modified_async(self, view):
        """Listens for modifications to views which are part of a currently
        active remote session."""
        global session
        if session is not None:
            if session.view == view:
                    current_buffer = view.substr(sublime.Region(0, view.size()))
                    print("diff")
                    session.send_diffs(current_buffer)

    def on_close(self, view):
        """Check to see if views I care about are closed, and if they are,
        drop them from my watched-views"""
        global session
        if session is not None:
            if session.view == view:
                session.close()
                session = None

class StartSessionCommand(sublime_plugin.TextCommand):
    """Command to start a new RemoteCollab session for the current view"""
    get_buffer = lambda view: view.substr(sublime.Region(0, view.size()))

    def run(self, edit):
        global session
        session = Session.Session(self.view)
        print ("[RemoteCollab] Started hosting session")

class ConnectToSessionCommand(sublime_plugin.WindowCommand):
    """Command to connect to an external RemoteCollab session."""

    def run(self):
        """
        Show the input panel to get an IP address for the remote host.
        """
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
        """
        Input panel handler - creates a new session connected to the given IP address.
        """
        global session
        session = Session.Session(self.window.new_file(), host=input)

class UpdateBufferCommand(sublime_plugin.TextCommand):
    """
    Command to create an Edit object and update the buffer.
    """
    def run(self, edit, new_buffer):
        self.view.replace(edit, sublime.Region(0, self.view.size()), new_buffer)

class DisconnectSessionCommand(sublime_plugin.ApplicationCommand):
    """Command to close a RemoteCollab session."""

    def run(self):
        global session
        session.close()
        session = None

