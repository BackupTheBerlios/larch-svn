#!/usr/bin/env python
#
# archinmain.py - archin main window
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
# 2008.02.01

# Add a Quit button?

from glob import glob
import gtk

from stage import Stage
from dialogs import popupError, popupMessage, popupWarning

class Archin(gtk.Window):
    def __init__(self):

        for m in glob("%s/modules/stages/*.py" % basePath):
            execfile(m, globals(), {})

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
        if not self.window:
            return
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
        while gtk.events_pending():
            gtk.main_iteration_do(False)

    def busy_off(self):
        if not self.window:
            return
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
        sclass = stages[stagename]
        sw = sclass()
        self.mainWidget.append_page(sw)
        self.setStage(sw)

    def setStage(self, sw):
        self.stage = sw
        self.lButton.set_label(sw.labelL())
        self.rButton.set_label(sw.labelR())
        n = self.mainWidget.get_n_pages()
        self.lButton.set_sensitive(n > 1)
        self.header.set_label('<span foreground="blue" size="20000">%s</span>'
                % self.stage.stageTitle())
        self.stage.show_all()
        self.mainWidget.set_current_page(-1)
        while gtk.events_pending():
            gtk.main_iteration(False)

    def help(self, widget, data=None):
        self.stage.help()

    def back(self, widget, data=None):
        """This goes back to the stage previous to the current one in the
        actually executed call sequence.
        """
        if install.gui_blocked:
            return
        n = self.mainWidget.get_n_pages()
        stage = self.mainWidget.get_nth_page(n-2)
        self.mainWidget.remove_page(n-1)
        stage.reinit()
        self.setStage(stage)

    def forward(self, widget, data=None):
        if install.gui_blocked:
            return
        self.stage.forward()
