#!/usr/bin/env python
#
# archin - A hard-disk installer for Arch Linux and larch
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
# 2008.01.17

# Add a Quit button?

import gtk, gobject
from stage import Stage
from glob import glob
from install import installClass
import os

stages = {}

class ArchinGtk(gtk.Window):
    def __init__(self):

        for m in glob("../share/modules/*.py"):
            execfile(m)

        gtk.Window.__init__(self)
        self.set_default_size(600,400)
        self.connect("destroy", gtk.main_quit)
        self.set_border_width(3)

        self.header = gtk.Label()
        self.header.set_use_markup(True)

        self.mainWidget = gtk.Notebook()
        self.mainWidget.set_show_tabs(False)

        self.lButton = gtk.Button(stock=gtk.STOCK_GO_BACK)
        self.rButton = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.hButton = gtk.Button(stock=gtk.STOCK_HELP)
        buttons = gtk.HButtonBox()
        buttons.pack_start(self.lButton)
        buttons.pack_start(self.hButton)
        buttons.pack_end(self.rButton)

        box1 = gtk.VBox()
        box1.pack_start(self.header, expand=False, padding=3)
        box1.pack_start(self.mainWidget)
        box1.pack_start(buttons, expand=False, padding=3)

        self.add(box1)

        self.hButton.connect("clicked", self.help)
        self.lButton.connect("clicked", self.back)
        self.rButton.connect("clicked", self.forward)

        self.watchcursor = gtk.gdk.Cursor(gtk.gdk.WATCH)

    def mainLoop(self):
        self.show_all()
        gtk.main()

    def busy(self):
#        gdk_win = gtk.gdk.Window(mainWindow.window,
#                gtk.gdk.screen_width(),
#                gtk.gdk.screen_height(),
#                gtk.gdk.WINDOW_CHILD,
#                0,
#                gtk.gdk.INPUT_ONLY)
#        gdk_win.set_cursor(self.watchcursor)
#        gdk_win.show()
        self.window.set_cursor(self.watchcursor)

# (*) I have commented out the sensitivity switch because it mucks up repeated
# clicks on a single button (the mouse must leave and reenter the button
# before clicking works again). gtk bug 56070
#        mainWindow.set_sensitive(False)
        gtk.main_iteration_do(False)

    def busy_off(self):
#        gdk_win.set_cursor(None)
#        gdk_win.destroy()
        self.window.set_cursor(None)

# See above (*)
#        mainWindow.set_sensitive(True)

    def goto(self, stagename):
        """This is the main function for entering a new stage.
        It stacks the widget (using a gtk.Notebook) so that it can be
        returned to later.
        """
        sw = stages[stagename]()
        self.mainWidget.append_page(sw)
        self.setStage(sw)

    def setStage(self, sw):
        self.stage = sw
        self.lButton.set_label(sw.labelL())
        self.rButton.set_label(sw.labelR())
        n = self.mainWidget.get_n_pages()
        self.lButton.set_sensitive(n > 1)

        gobject.idle_add(self.setpage)

        self.header.set_label('<span foreground="blue" size="20000">%s</span>'
                % self.stage.stageTitle())
        self.stage.show_all()

    def setpage(self):
        self.mainWidget.set_current_page(-1)
        return False

    def help(self, widget, data=None):
        self.stage.help()

    def back(self, widget, data=None):
        """This goes back to the stage previous to the current one in the
        actually executed call sequence.
        """
        n = self.mainWidget.get_n_pages()
        stage = self.mainWidget.get_nth_page(n-2)
        self.mainWidget.remove_page(n-1)
        stage.reinit()
        self.setStage(stage)

    def forward(self, widget, data=None):
        self.stage.forward()

def popupError(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin Error"))
    dialog.run()
    dialog.destroy()

def popupMessage(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin"))
    dialog.run()
    dialog.destroy()

def popupWarning(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin"))
    res = (dialog.run() == gtk.RESPONSE_YES )
    dialog.destroy()
    return res

def end():
    print "Exiting"
    quit()

if (__name__ == "__main__"):
    import __builtin__
    def tr(s):
        return s
    __builtin__._ = tr

    import sys
    if (len(sys.argv) == 1):
        target = None
    elif (len(sys.argv) == 2):
        target = sys.argv[1]
    else:
        print "ERROR: too many arguments. Usage:"
        print "          archin.py [target-address]"
        sys.exit(1)

    __builtin__.mainWindow = ArchinGtk()
    __builtin__.install = installClass(target)
    mainWindow.goto('welcome')
    mainWindow.mainLoop()
