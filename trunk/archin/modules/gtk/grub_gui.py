# grub_gui.py - extra widgets for the grub stage
#
# (c) Copyright 2008 Michael Towers <gradgrind[at]online[dot]de>
#
# This file is part of the larch project.
#
#    larch is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    larch is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with larch; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#----------------------------------------------------------------------------
# 2008.02.10

import gtk

class Mbrinstall(gtk.Frame):
    """
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        self.master = master
        self.set_border_width(20)

        self.mlcombobox = gtk.HBox(spacing=5)
        self.mlcombobox.set_border_width(5)
        l = gtk.Label(_("Select menu.lst to import: "))
        self.mlcombobox.pack_start(l, False)
        self.mlcombo = gtk.combo_box_new_text()
        self.mlcombo.connect("changed", mainWindow.sigprocess, self.newimport)
        self.mlcombo.append_text(_("None"))
        for d, p in install.menulst:
            self.mlcombo.append_text("%s:%s" % (d, p))
        self.mlcombobox.pack_start(self.mlcombo, False)

        eb = gtk.Button(_("Edit menu.lst"))
        eb.connect("clicked", self.editmbr)
        self.mlcombobox.pack_end(eb, False)

        self.add(self.mlcombobox)
        self.show_all()

    def set_enabled(self, on):
        if on:
            self.mlcombo.set_active(0)
        else:
            self.mlcombo.set_active(-1)
        self.set_sensitive(on)

    def newimport(self, data=None):
        if (self.mlcombo.get_active() <= 0):
            at = None
        else:
            at = self.mlcombo.get_active_text()
        self.master.setimport_cb(at)

    def editmbr(self, widget, data=None):
        # Start the editor.
        self.master.editmbr_cb()


class Oldgrub(gtk.Frame):
    """
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        self.set_border_width(20)
        self.master = master

        self.mlcombobox = gtk.HBox(spacing=5)
        self.mlcombobox.set_border_width(5)
        l = gtk.Label(_("Select menu.lst to use: "))
        self.mlcombobox.pack_start(l, False)
        self.mlcombo = gtk.combo_box_new_text()
        self.mlcombo.connect("changed", mainWindow.sigprocess, self.newml)
        for d, p in install.menulst:
            self.mlcombo.append_text("%s:%s" % (d, p))
        self.mlcombobox.pack_start(self.mlcombo, False)

        eb = gtk.Button(_("Edit menu.lst"))
        eb.connect("clicked", self.editml)
        self.mlcombobox.pack_end(eb, False)

        self.add(self.mlcombobox)
        self.set_enabled(False)
        self.show_all()

    def set_enabled(self, on):
        if on:
            self.mlcombo.set_active(0)
        else:
            self.mlcombo.set_active(-1)
        self.set_sensitive(on)

    def newml(self, widget, data=None):
        self.master.setml_cb(self.mlcombo.get_active_text())

    def editml(self, widget, data=None):
        # Start the editor.
        self.master.editml_cb()
