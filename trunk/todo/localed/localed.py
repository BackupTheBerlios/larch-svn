#!/usr/bin/env python
#
# localed - A gui to configure supported locales in Arch Linux
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
# 2008.03.11

import os, sys
import gtk

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Localed(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False)
        header = gtk.Label()
        header.set_markup(_("<b>Configure supported locales</b>"))
        self.pack_start(header)
        hbox = gtk.HBox(False)
        self.pack_start(hbox)

        self.sel_listbox = gtk.TreeView()
        # ...

        hbox.pack_start(self.sel_listbox)

    def tidyup(self):
        print "tidy up!"


def popupError(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_text(text)
    dialog.set_title(_("localed Error"))
    dialog.run()
    dialog.destroy()


if __name__ == '__main__':
    def exit(widget=None, data=None):
        widget.tidyup()
        gtk.main_quit()

    import __builtin__
    def tr(s):
        return s
    __builtin__._ = tr

    if (len(sys.argv) == 1):
        rootdir = ''
    elif (len(sys.argv) == 2):
        rootdir = sys.argv[1]
    else:
        popupError(_("Usage:\n"
            "          localed.py [system root directory (default is '/')]\n"),
            _("Bad arguments"))
        quit()
    localegen = rootdir + '/etc/locale.gen'
    if not os.path.isfile(localegen):
        popupError(_("File '%s' not found") % localegen,
            _("Bad arguments"))
        quit()

    widget = Localed()
    mainWindow = gtk.Window()
    mainWindow.set_default_size(600,400)
    mainWindow.connect("destroy", exit)
    mainWindow.set_border_width(3)
    mainWindow.add(widget)
    mainWindow.show_all()
    gtk.main()

