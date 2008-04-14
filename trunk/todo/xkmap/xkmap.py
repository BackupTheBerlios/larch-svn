#!/usr/bin/env python
#
# xkmap.py   --  Simple GUI for 'setxkbmap'
#
# Copyright (C) 2006-2008  Michael Towers
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#-------------------------------------------------------------------
# Version 2.0 // 14th April 2008

# Set this for your system (probably one of these is OK)
base_lst = "/usr/share/X11/xkb/rules/base.lst"
#base_lst = "/etc/X11/xkb/rules/base.lst"
#base_lst = "/usr/lib/X11/xkb/rules/base.lst"

# This file allows automatic editing of a 'setxkbmap' command - a line
# containing 'setxkbmap' will be replaced by the new version.
SKBPATH = "/etc/X11/xinit/xinitrc.custom"
#-------------------------------------------------------------------

import os, sys
from subprocess import Popen, PIPE, STDOUT

# For running utilities as root:
import pexpect

import gtk, pango

# The not yet implemented i18n bit ...
import __builtin__
def tr(s):
    return s
__builtin__._ = tr


abouttext = _('<i>xkmap</i> is a simple gui front-end for <i>setxkbmap</i>,'
                ' for setting the keyboard mapping for the Xorg graphical'
                ' windowing system. It was designed for <i>larch</i> \'live\''
                ' systems but should work on most linux systems.\n'
                'To keep it simple it doesn\'t support all the options'
                ' which are available for keyboard configuration, but just'
                ' allows setting of the model, layout and variant.\n\n'
                'This program was written for the <i>larch</i> project:\n'
                '       http://larch.berlios.de\n'
                '\nIt is free software,'
                ' released under the GNU General Public License.\n')


helptext = _("""
""")


class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        #self.set_default_size(400,300)
        self.connect("destroy", self.exit)
        self.set_border_width(3)

        # Root password
        self.password = None

        self.notebook = gtk.Notebook()
        self.add(self.notebook)
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.show_tabs = True
        self.notebook.show_border = False

        self.setup()

    def init(self, maintabtitle, configure=False):
        self.maintab = MainTab()
        self.notebook.append_page(self.maintab, gtk.Label(maintabtitle))
        if configure:
            self.notebook.append_page(Configure(), gtk.Label(_("Configure")))
        self.notebook.append_page(Help(), gtk.Label(_("Help")))
        self.notebook.append_page(About(), gtk.Label(_("About")))

        self.notebook.set_current_page(0)

    def mainLoop(self):
        self.show_all()
        gtk.main()

    def exit(self, widget=None, data=None):
        self.pending()
        gtk.main_quit()

    def rootrun(self, cmd):
        """Run the given command as 'root'.
        Return a pair (completion code, output).
        """
        # If not running as 'root' use pexpect to use 'su' to run the command
        if (os.getuid() == 0):
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            o = p.communicate()[0]
            return (p.returncode, o)
        else:
            if not self.password:
                pw = popupRootPassword()
                if (pw == None):
                    return (1, _("You cancelled the operation."))
                cc, mess = asroot('true', pw)
                if (cc != 0):
                    return (cc, mess)
                self.password = pw
            return asroot(cmd, self.password)

    def setup(self):
        """This function is called during initialization of the main window.
        It can be used for setting up instance variables, etc.
        """
        pass

    def pending(self):
        """This function is called just before quitting the program.
        It can be used to do tidying up.
        """
        pass


def popupRootPassword():
    dialog = gtk.Dialog(parent=gui,
            flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    label = gtk.Label(_("To complete this operation you must enter"
            " the root (administrator) password:"))
    label.set_line_wrap(True)
    label.set_alignment(0.0, 0.5)
    dialog.vbox.pack_start(label)
    label.show()
    entry = gtk.Entry(max=20)
    entry.set_visibility(False)
    dialog.vbox.pack_start(entry)
    entry.show()
    entry.connect('activate', enterKey_cb, dialog)
    if (dialog.run() == gtk.RESPONSE_ACCEPT):
        val = entry.get_text()
    else:
        val = None
    dialog.destroy()
    return val

def enterKey_cb(widget, dialog):
    """A callback for the Enter key in dialogs.
    """
    dialog.response(gtk.RESPONSE_ACCEPT)

def asroot(cmd, pw):
    """Run a command as root, using the given password.
    """
    child = pexpect.spawn('su -c "%s"' % cmd)
    child.expect(':')
    child.sendline(pw)
    child.expect(pexpect.EOF)
    o = child.before.strip()
    return (0 if (o == '') else 1, o)


class Help(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.view = gtk.TextView()
        self.view.set_editable(False)
        #view.set_wrap_mode(gtk.WRAP_WORD)
        sw.add(self.view)
        self.add(sw)
        self.view.show()

        self.reportbuf = self.view.get_buffer()
        self.reportbuf.set_text(helptext)


class About(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        box = gtk.VBox()
        box.set_border_width(10)
        label = gtk.Label()
        label.set_line_wrap(True)
        #label.set_alignment(0.0, 0.5)
        label.set_markup(abouttext + '\nCopyright (c) 2008   Michael Towers')
        box.pack_start(label)
        self.add(box)


class Configure(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(10)
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_markup(_('<b>Not Yet implemented</b>'))
        self.add(label)



class MainTab(gtk.VBox):

    def __init__ (self):
        gtk.VBox.__init__(self, spacing=5)
        title = gtk.Label()
        title.set_markup('<span size="xx-large">%s</span>' %
                _("Set Keyboard Mapping"))
        self.pack_start(title, False)

        self.pack_start(gtk.HSeparator(), False)

        self.modelframe = XCombo(_("Model"))
        self.pack_start(self.modelframe, False)

        self.layoutframe = XCombo(_("Layout"))
        self.pack_start(self.layoutframe, False)

        self.variantframe = XCombo(_("Variant"))
        self.pack_start(self.variantframe, False)

        buttons = gtk.HButtonBox()
        buttons.set_direction(gtk.TEXT_DIR_NONE)
        buttons.set_layout(gtk.BUTTONBOX_END)
        buttons.set_border_width(3)
        buttons.set_spacing(5)
        self.pack_end(buttons, False)

        but_apply = gtk.Button(stock=gtk.STOCK_APPLY)
        buttons.add(but_apply)
        but_apply.connect('clicked', self.apply)
        but_quit = gtk.Button(stock=gtk.STOCK_QUIT)
        buttons.add(but_quit)
        but_quit.connect('clicked', gui.exit)

        self.init_combos()





        return

    def init_combos(self):
        self.modelframe.set_list(i_xkbset.models)
        self.modelframe.select(i_xkbset.model)
        return

        # Read the glade file
        self.wTree = gtk.glade.XML("/usr/share/xkmap.glade")

        # Create a dictionay of connections, then autoconnect
        dic = { "on_window1_destroy"  : gtk.main_quit,
                "on_btCancel_clicked" : gtk.main_quit,
                "on_btApply_clicked"  : self.change,
                "on_btOK_clicked"     : self.changeq,
                "on_cbModel_changed"  : self.model,
                "on_cbLayout_changed" : self.layout,
                "on_cbVariant_changed": self.variant
              }
        self.wTree.signal_autoconnect(dic)

        # To prevent error message
        self.cbVariant = None

        # Set up comboboxes
        # Model
        cellm = gtk.CellRendererText()
        self.modelModel = gtk.ListStore(str)
        self.cbModel = self.wTree.get_widget("cbModel")
        self.cbModel.set_model(self.modelModel)
        self.cbModel.pack_start(cellm, True)
        self.cbModel.set_attributes(cellm, text=0)

        i = 0
        for item in i_xkbset.models:   # item list is a list of strings
            self.modelModel.append([item])
            if item.split(None , 1)[0] == i_xkbset.model:
                self.iModel = i
            i += 1
        self.cbModel.set_active(self.iModel)

        # Layout
        celll = gtk.CellRendererText()
        self.modelLayout = gtk.ListStore(str)
        self.cbLayout = self.wTree.get_widget("cbLayout")
        self.cbLayout.set_model(self.modelLayout)
        self.cbLayout.pack_start(celll, True)
        self.cbLayout.set_attributes(celll, text=0)

        i = 0
        for item in self.i_xkbset.layouts:   # item list is a list of strings
            self.modelLayout.append([item])
            if item.split(None , 1)[0] == self.i_xkbset.layout:
                self.iLayout = i
            i += 1
        self.cbLayout.set_active(self.iLayout)

        # Variant -- this depends on the chosen Layout!
        cellv = gtk.CellRendererText()
        self.modelVariant = gtk.ListStore(str)
        self.cbVariant = self.wTree.get_widget("cbVariant")
        self.cbVariant.set_model(self.modelVariant)
        self.cbVariant.pack_start(cellv, True)
        self.cbVariant.set_attributes(cellv, text=0)

        self.showVariants ()

    def showVariants (self):
        self.modelVariant.clear ()
        layout = self.i_xkbset.layouts[self.iLayout].split ()[0]
        self.variants = self.i_xkbset.allVariants[layout]
        self.iVariant = 0
        i = 0
        for item in self.variants:   # item list is a list of strings
            self.modelVariant.append([item])
            if item.split(None , 1)[0] == self.i_xkbset.variant:
                self.iVariant = i
            i += 1
        self.cbVariant.set_active(self.iVariant)



    def apply(self, widget, data=None):
        print "NYI"


    def change (self, widget):
        self.i_xkbset.new ()

    def changeq (self, widget):
        self.change (widget)
        gtk.main_quit ()

    def model (self, widget):
        i = self.cbModel.get_active()
        if i != self.iModel:
            self.iModel = i
            self.i_xkbset.model = self.i_xkbset.models[i].split(None , 1)[0]

    def layout (self, widget):
        i = self.cbLayout.get_active()
        if i != self.iLayout:
            self.iLayout = i
            self.i_xkbset.layout = self.i_xkbset.layouts[i].split(None , 1)[0]
            self.showVariants ()
        self.variant(None)

    def variant (self, widget):
        if not self.cbVariant:
            # To prevent error message
            return
        i = self.cbVariant.get_active()
        if (i != self.iVariant) or (widget == None):
            self.iVariant = i
            self.i_xkbset.variant = self.variants[i].split(None , 1)[0]


    def mainloop (self):
        gtk.main ()



class xkbset:
    def __init__ (self):
        self.configfile = os.path.expanduser("~/.xkmap")
        # default values
        self.model = "pc101"
        self.layout = "us"
        self.variant = "Standard"
        if os.path.isfile (self.configfile):
            f = open (self.configfile)
            self.model, self.layout, self.variant = f.readline ().strip ().split ("|")
            f.close ()

        # Read 'base.lst'
        blf = open(base_lst)
        while blf.readline().strip() != "! model": pass

        self.models = []
        while True:
            line = blf.readline().strip()
            if not line: continue
            if line == "! layout": break
            self.models.append (line)

        self.layouts = []
        while True:
            line = blf.readline().strip()
            if not line: continue
            if line == "! variant": break
            self.layouts.append (line)

        self.layouts.sort()

        self.allVariants = {}
        while True:
            line = blf.readline().strip()
            if not line: continue
            if line == "! option": break
            parts = line.split (None, 2)
            line = parts[0] + " - " + parts[2]
            layout = parts[1].rstrip (":")
            if not self.allVariants.has_key (layout):
                self.allVariants[layout] = [ "Standard" ]
            self.allVariants[layout].append (line)

        blf.close()


    def new (self):
        m = self.model
        l = self.layout
        v = self.variant
        if v == "Standard":
            v = '""'

        command = "setxkbmap -rules xorg -model %s -layout %s -variant %s" % (m, l, v)
        print command
        os.system (command)
        os.system ('sed "s|.*setxkbmap.*|%s|" -i %s' % (command, SKBPATH))

        f = open (self.configfile, "w")
        f.write ("%s|%s|%s\n" % (self.model, self.layout, self.variant))
        f.close ()


class XCombo(gtk.Frame):
    def __init__(self, label=None):
        gtk.Frame.__init__(self, label)
        self.combo = gtk.ComboBox()
        # Need some space around the combo box. The only way I've found
        # of doing this (so far) is to add an extra layout widget ...
        border = gtk.Table()
        border.attach(self.combo, 0, 1, 0, 1, xpadding=3, ypadding=3)
        self.add(border)

        self.list = gtk.ListStore(str, str)
        self.combo.set_model(self.list)
        cell1 = gtk.CellRendererText()
        #cell1.set_fixed_size(80, -1)
        cell1.set_property('width-chars', 15)
        #cell1.set_property('cell-background', 'red')
        cell1.set_property('ellipsize', pango.ELLIPSIZE_END)
        self.combo.pack_start(cell1, expand=False)
        self.combo.add_attribute(cell1, 'text', 0)
        cell2 = gtk.CellRendererText()
        cell2.set_property('foreground', '#00a080')
        self.combo.pack_start(cell2)
        self.combo.add_attribute(cell2, 'text', 1)

#        self.blocked = False
#        self.combo.connect('changed', self.changed_cb)

    def set_list(self, values):
        self.blocked = True
        self.list.clear()
        for v in values:
            a, b = v.split(None, 1)
            self.list.append([a, b])
        while gtk.events_pending():
            gtk.main_iteration(False)
        self.blocked = False

# Maybe I don't need a callback?
    def changed_cb(self, widget, data=None):
        if self.blocked:
            return
        i = self.combo.get_active()
        v = self.list[i][0]

    def getval(self):
        """Return the selected value (first column only).
        """
        return self.list[self.combo.get_active()][0]

    def select(self, val):
        """Programmatically set the currently selected entry.
        """
        i = 0
        for u in self.list:
            if (u[0] == val):
                self.combo.set_active(i)
                break
            i += 1




if __name__ == "__main__":
    i_xkbset = xkbset ()
#    i_gui = gui (i_xkbset)
#    i_gui.mainloop ()



    gui = MainWindow()
    gui.init(_("Key Maps"))
    gui.mainLoop()

