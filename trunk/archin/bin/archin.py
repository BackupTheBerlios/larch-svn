#!/usr/bin/env python
#
# 2008.01.17

# Add a Quit button?

import gtk, gobject
from stage import Stage
from glob import glob
from install import installClass
from embterm import terminal
import os

stages = {}

class ArchinGtk(gtk.Window):
    def __init__(self):

        for m in glob("modules/*.py"):
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

    def mainLoop(self):
        self.show_all()
        gtk.main()

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
