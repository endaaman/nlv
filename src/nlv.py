# nlv.py
#
# Copyright (c) 2017 endaaman
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.

import os, sys
import string
import random
import signal
from xml.etree import ElementTree
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, GdkPixbuf, Gdk
from meta import VERSION, PACKAGE_NAME
from comment import CommentEntry, CommentList
from nico import Nico


def rand_str(n = 5):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])

class App:
    def __init__(self):
        self.nico = Nico()
        self.combo_data = None

        self.nico.load_lives()
        self.build_layout()
        self.window.show_all()

    def build_layout(self):
        self.window = Gtk.Window()
        self.window.set_title('nlv')
        self.window.set_border_width(6)
        self.window.resize(300, 600)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.entry = Gtk.Entry()
        self.entry.set_text("")

        self.combo = Gtk.ComboBox()
        self.combo.set_entry_text_column(0)

        self.comment_list = CommentList()
        tmps = [
            ('person1', 'hoge fuga piyo hoge fuga piyo hoge fuga piyo hoge fuga piyo'),
            ('person2', 'hoge fuga piyo')
        ]
        for tmp in tmps:
            self.comment_list.insert_entry(CommentEntry(tmp[0], tmp[1]))

        self.update_lives()
        renderer_text = Gtk.CellRendererText()
        self.combo.pack_start(renderer_text, True)
        self.combo.add_attribute(renderer_text, 'text', 0)

        self.vbox.pack_start(self.entry, False, False, 0)
        self.vbox.pack_start(self.combo, False, False, 0)
        self.vbox.pack_start(self.comment_list, True, True, 0)
        self.window.add(self.vbox)

        self.window.connect('delete-event', self.on_window_destroy)
        self.combo.connect('changed', self.on_combo_changed)
        self.entry.connect('activate', self.on_entry_activate)

    def update_lives(self):
        if self.combo_data:
            self.combo_data.clear()
        self.combo_data = Gtk.ListStore(str, str)
        for id, live in self.nico.lives.items():
            self.combo_data.append([live.title, live.id])
        self.combo.set_model(self.combo_data)

    def on_window_destroy(self, window: Gtk.Window, event):
        Gtk.main_quit()

    def on_combo_changed(self, combo: Gtk.ComboBoxText):
        self.comment_list.clear()
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            self.entry.set_text(model[tree_iter][1])
            self.open_live(model[tree_iter][1])

    def select_combo_item(self, id):
        index = 0
        for model in self.combo_data:
            if id == model[1]:
                self.combo.set_active(index)
                return
            index = index + 1

    def on_entry_activate(self, entry):
        id = self.entry.get_text()
        self.nico.load_live(id)
        self.update_lives()
        self.select_combo_item(id)

    def open_live(self, id):
        self.sock = self.nico.connect(id)
        self.gen = self.sock.recieve()
        GObject.timeout_add(100, self.read_comment)

    def read_comment(self):
        if not self.sock:
            print('abort')
            return False
        print(next(self.gen))
        GObject.timeout_add(100, self.read_comment)
        # for line in raw:
        #     el = ElementTree.fromstring(line)
        #     if el is None:
        #         continue
        #     chat = el.find('.//chat')
        #     entry = CommentEntry(
        #         el.get('user_id'),
        #         el.text,
        #         el.get('premium') == '1' and True or False,
        #     )
        #     self.comment_list.insert_entry(entry)
        # <chat thread="1611067860" no="36" vpos="72617" date="1504454887" date_usec="300315" mail="184" user_id="J-5AfWO5HP63nwg43FmoC7u2g68" anonymity="1">はや</chat><chat thread="1611067860" no="37" vpos="73137" date="1504454892" date_usec="399014" mail="184" user_id="vwMC_-jZ1RsDbbxKruxPFr02BKA" premium="1" anonymity="1">はやいな</chat>



def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = App()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
