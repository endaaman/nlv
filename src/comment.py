# comment.py
#
# Copyright (c) 2017 endaaman
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import signal


class CommentEntry(Gtk.ListBoxRow):
    def __init__(self, user_name, message, is_premium = False):
        super().__init__()

        label_username = Gtk.Label()
        label_username.set_markup("<small>%s</small>" % user_name)
        label_username.set_justify(Gtk.Justification.LEFT)
        label_username.set_alignment(0, 0.5)

        label_message = Gtk.Label(message)
        label_message.set_justify(Gtk.Justification.LEFT)
        label_message.set_alignment(0, 0.5)
        label_message.set_line_wrap(True)

        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(label_username, True, True, 2)
        hbox.pack_start(label_message, True, True, 0)
        self.add(hbox)

class CommentList(Gtk.ListBox):
    def __init__(self):
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.entries = []
        pass

    def insert_entry(self, entry: CommentEntry):
        self.entries.append(entry)
        self.insert(entry, 0)
        self.select_row(entry)

    def clear(self):
        for entry in self.entries:
            self.remove(entry)
            self.entries = []
