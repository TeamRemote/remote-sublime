Remote Collab for SublimeText 
=============================

[![Build Status](https://travis-ci.org/TeamRemote/remote-sublime.svg?branch=master)](https://travis-ci.org/TeamRemote/remote-sublime)

Remote Collab is an open-source SublimeText plugin for remote pair programming, allowing multiple developers to work together on the same project in real-time.

How to Install
--------------

#### Via Package Control

The easiest way to install is using [Sublime Package Control](https://sublime.wbond.net/).

1. Open Command Palette using menu item `Tools -> Command Palette...` (<kbd>⇧</kbd><kbd>⌘</kbd><kbd>P</kbd> on Mac)
2. Choose `Package Control: Install Package`
3. Find `RemoteCollab` and hit <kbd>Enter</kbd>

#### Manual

You can also install Remote Collab manually:

1. Download the .zip or .tar.gz archive
2. Unzip and rename the folder to `RemoteCollab`
3. Copy the folder into `Packages` directory, which you can find using the menu item `Sublime Text -> Preferences -> Browse Packages...`

How to Use
----------

#### Host a session

1. Open the file you wish to collaboratively edit
2. Open Command Palette using menu item `Tools -> Command Palette...` (<kbd>⇧</kbd><kbd>⌘</kbd><kbd>P</kbd> on Mac)
3. Choose `Remote: Host Session`
4. You are now hosting a Remote Collab session. Give your IP address to the remote colleage you wish to collaborate with and they can join your session.

#### Join a session

1. Open Command Palette using menu item `Tools -> Command Palette...` (<kbd>⇧</kbd><kbd>⌘</kbd><kbd>P</kbd> on Mac)
2. Choose `Remote: Connect to Session`
3. Enter the IP address of the host whose session you wish to connect to.
4. You are now collaboratively editing a document with the host!

Team Remote
-----------

Team Remote is Hawk Weisman (@hawkw), Dibyojyoti Mukherjee (@dibyom), Soukaina Hamimoune (@hamimounes), and Andreas Bach Landgrebe (@grebes15). We are students at Allegheny College.
