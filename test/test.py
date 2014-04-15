import sublime
from unittest import TestCase

version = sublime.version()

class TestDiffListener(TestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().run_command("close_file")

    # put actual tests here