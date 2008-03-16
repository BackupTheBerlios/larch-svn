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
# 2008.03.16

import os, sys, re, time
from subprocess import Popen, PIPE
import gtk

STARTFLAG = "###+++ autogen"
ENDFLAG = "###--- autogen"

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Localed(gtk.VBox):
    def __init__(self, sysbase):
        self.localegen = sysbase + '/etc/locale.gen'
        if not os.path.isfile(self.localegen):
            popupError(_("File '%s' not found") % self.localegen,
                _("Bad arguments"))
            quit()
        self.rcconf = sysbase + '/etc/rc.conf'

        gtk.VBox.__init__(self, False)
        header = gtk.Label()
        header.set_markup(_("<b><big>Configure supported locales</big></b>"))
        self.pack_start(header, False, padding=20)
        hbox = gtk.HBox(False, spacing=5)
        self.pack_start(hbox)

        self.sublistbox = SubListBox(_("Supported"), _("Unsupported"))
        hbox.pack_start(self.sublistbox)

        sep1 = gtk.VSeparator()
        hbox.pack_start(sep1)

        vbox = gtk.VBox(False, spacing=5)
        hbox.pack_start(vbox)

        tframe = gtk.Frame()
        scroll = gtk.ScrolledWindow()
        scroll.set_border_width(5)
        tframe.add(scroll)
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        scroll.add(self.textview)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.set_size_request(250, 250)
        vbox.pack_start(tframe)

        frame = gtk.Frame()
        frame.set_label(_("System locale"))
        self.combolist = gtk.ListStore(str)
        self.lcombo = gtk.ComboBoxEntry(self.combolist, 0)
        self.lcomboentry = self.lcombo.child
        self.lcomboclr0 = self.lcomboentry.get_style().text[gtk.STATE_NORMAL]
        self.lcomboclr1 = gtk.gdk.color_parse('#FF0000')
        self.lcomboentry.connect('changed', self.entry_cb)
        #doesn't work: self.lcombo.set_border_width(5)
        pbox = gtk.Table()
        pbox.attach(self.lcombo, 0, 1, 0, 1, xpadding=5, ypadding=5)

        frame.add(pbox)
        vbox.pack_start(frame, False)

        bbox = gtk.HButtonBox()
        vbox.pack_end(bbox, False)
        bbox.set_layout(gtk.BUTTONBOX_END)
        rbutton = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        rbutton.connect('clicked', self.revert_cb)
        bbox.add(rbutton)
        cbutton = gtk.Button(stock=gtk.STOCK_CANCEL)
        cbutton.connect('clicked', exit)
        bbox.add(cbutton)
        abutton = gtk.Button(stock=gtk.STOCK_APPLY)
        abutton.connect('clicked', self.apply_cb)
        bbox.add(abutton)

        self.process = None

    def readlocales(self):
        self.sublistbox.clear()
        self.cleanfile = ''     # build up a fully commented-out template
        locales = []    # list of locales, also used for duplicate checking
        lactive = []    # list of 'active/selected' flags for locales
        mask = False    # flag used to skip over automatically generated lines

        rx = re.compile("[#]? *([a-z][a-z]_.*)")
        fh = open(self.localegen, "r")
        for line in fh:
            l = line.strip()
            if l.startswith(STARTFLAG):
                mask = True
                continue
            elif l.startswith(ENDFLAG):
                mask = False
                continue
            rm = rx.match(l)
            active = (l != '') and not l.startswith('#')
            if rm:
                val = rm.group(1)
                if not val in locales:
                    locales.append(val)
                    lactive.append(active)
            if mask:
                continue
            if active:
                l = '#' + l
            self.cleanfile += l + '\n'
        fh.close()
        #print self.cleanfile

        # add locales to widget, after sorting (just in case ...)
        l0 = [(locales[i], lactive[i]) for i in range(len(locales))]
        l0.sort()
        for l, a in l0:
            self.sublistbox.additem(l, a)

        self.listUpdated()

    def tidyup(self):
        print "tidy up!"

    def getlocalenames(self):
        """Fetch a list of locale names suitable for use in rc.conf setting
        ('LOCALE'). This is not exhaustive, it just modifies the locales
        in the 'supported' list and adds 'POSIX' and 'C'.
        """
        ll = self.sublistbox.getsupported()
        lnl = ['C', 'POSIX']
        for l in ll:
            ln = l.split()[0]
            lnc = ln.split('.')
            if (len(lnc) > 1):
                ln = lnc[0] + '.' + lnc[1].lower().replace('-', '')
            lnl.append(ln)
        return lnl

    def entry_cb(self, w, data=None):
        # The text in the entry is painted red when it is not in the list,
        # but should it be more flexible?
        current = self.lcomboentry.get_text()
        if current in self.getlocalenames():
            self.lcomboentry.modify_text(gtk.STATE_NORMAL, self.lcomboclr0)
        else:
            self.lcomboentry.modify_text(gtk.STATE_NORMAL, self.lcomboclr1)

    def listUpdated(self):
        locales = self.getlocalenames()
        self.combolist.clear()
        for l in locales:
            self.combolist.append((l,))

        self.entry_cb(self.lcomboentry)

    def getcurrent(self):
        locale = None
        fh = open(self.rcconf, "r")
        for line in fh:
            l = line.strip()
            lsplit = l.split('=', 1)
            if (len(lsplit) != 2) or (lsplit[0] != 'LOCALE'):
                continue
            locale = lsplit[1]
            if (((locale[0] == '"') and (locale[-1] == '"')) or
                    ((locale[0] == "'") and (locale[-1] == "'"))):
                locale = locale[1:-1]
            break
        fh.close()

        if (locale == None):
            popupError(_("No locale in %s!!!") % filepath)
            exit()

        self.lcomboentry.set_text(locale)

    def output(self, text):
        buf = self.textview.get_buffer()
        iter = buf.get_end_iter()
        buf.insert(iter, text)

    def revert_cb(self, w=None, data=None):
        if self.process:
            return
        self.readlocales()
        self.getcurrent()

    def apply_cb(self, w, data=None):
        # Generate locales
        # Ideally this should start the process and set up a callback to
        # print the output when it is available (line-by-line)
        if self.process:
            return

        # Edit locale.gen
        os.rename(self.localegen, self.localegen + '.old')
        fh = open(self.localegen, "w")
        fh.write(STARTFLAG + "\n")
        for l in self.sublistbox.getsupported():
            fh.write(l + "\n")
        fh.write(ENDFLAG + "\n")
        fh.write(self.cleanfile)
        fh.close()

        self.process = Popen(['chroot', rootdir, 'locale-gen'], stdout=PIPE)
        fd = self.process.stdout.fileno()

        active = True
        while active:
            active = (self.process.poll() == None)
            op = os.read(fd, 100)
            if op:
                self.output(op)
                while gtk.events_pending():
                   gtk.main_iteration(False)

            time.sleep(0.1)
        self.process = None

        # Edit rc.conf
        os.system("sed -i 's|^LOCALE=.*|LOCALE=\"%s\"|' %s" %
                (self.lcomboentry.get_text(), self.rcconf))



def popupError(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_text(text)
    dialog.set_title(_("localed Error"))
    dialog.run()
    dialog.destroy()


class SubListBox(gtk.HBox):
    def __init__(self, header1=None, header2=None):
        gtk.HBox.__init__(self, False)
        columnwidth = 150

        # create a ListStore with one string column and one boolean (filter)
        # column to use as the model
        self.liststore = gtk.ListStore(str, bool)

        # 1st list ('supported')
        sw_sel = gtk.ScrolledWindow()
        sw_sel.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw_sel.set_shadow_type(gtk.SHADOW_IN)
        sw_sel.set_size_request(columnwidth, -1)

        self.sel_filter = self.liststore.filter_new()
        self.sel_filter.set_visible_column(1)

        # create the 'selected' TreeView using filtered liststore
        self.sel_view = gtk.TreeView(self.sel_filter)

        # create a CellRenderer to render the data
        self.cell = gtk.CellRendererText()

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn(header1, self.cell, text=0)

        # add column to treeview
        self.sel_view.append_column(self.tvcolumn)

        # place treeview in scrolled window
        sw_sel.add(self.sel_view)

        # add scrolled window to hbox
        self.pack_start(sw_sel)

        # Transfer-buttons
        bt_sel = gtk.Button()
        larrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        bt_sel.add(larrow)
        bt_sel.connect("clicked", self.tosel)
        bt_unsel = gtk.Button()
        rarrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        bt_unsel.add(rarrow)
        bt_unsel.connect("clicked", self.tounsel)
        vbox = gtk.VBox(False, spacing=20)
        alignment = gtk.Alignment(yalign=0.5)
        alignment.add(vbox)
        self.pack_start(alignment, False, padding=5)
        vbox.pack_start(bt_sel, False)
        vbox.pack_start(bt_unsel, False)


        # 2nd list ('unsupported')
        sw_unsel = gtk.ScrolledWindow()
        sw_unsel.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw_unsel.set_shadow_type(gtk.SHADOW_IN)
        sw_unsel.set_size_request(columnwidth, -1)

        self.unsel_filter = self.liststore.filter_new()
        self.unsel_filter.set_visible_func(self.unselected)

        # create the 'selected' TreeView using filtered liststore
        self.unsel_view = gtk.TreeView(self.unsel_filter)

        # create the TreeViewColumn to display the data
        self.tvcolumn2 = gtk.TreeViewColumn(header2, self.cell, text=0)

        # add column to treeview
        self.unsel_view.append_column(self.tvcolumn2)

        # place treeview in scrolled window
        sw_unsel.add(self.unsel_view)

        # add scrolled window to hbox
        self.pack_start(sw_unsel)

        self.sel_selection = self.sel_view.get_selection()
        self.sel_selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.unsel_selection = self.unsel_view.get_selection()
        self.unsel_selection.set_mode(gtk.SELECTION_MULTIPLE)

    def clear(self):
        self.liststore.clear()

    def additem(self, text, sel):
        self.liststore.append((text, sel))

    def unselected(self, model, iter, user_data=None):
        """A filter function, just negates the boolean column in the
        list model.
        """
        return not model.get_value(iter, 1)

    def selectedpaths(self, sel):
        model, pathlist = sel.get_selected_rows()
        return pathlist

    def getsupported(self):
        """Get the names of the locales in the 'supported' view.
        """
        return [r[0] for r in self.sel_filter]

    # These two functions move entries between lists. I collect iters to
    # all affected self.liststore entries before making any changes because
    # I expect a change will affect the paths in the filtered stores.
    def tosel(self, w, data=None):
        iters = []
        for path in self.selectedpaths(self.unsel_selection):
            iter = self.unsel_filter.get_iter(path)
            iters.append(self.unsel_filter.convert_iter_to_child_iter(iter))

        for i in iters:
            self.liststore.set_value(i, 1, True)

        widget.listUpdated()

    def tounsel(self, w, data=None):
        iters = []
        for path in self.selectedpaths(self.sel_selection):
            iter = self.sel_filter.get_iter(path)
            iters.append(self.sel_filter.convert_iter_to_child_iter(iter))

        for i in iters:
            self.liststore.set_value(i, 1, False)

        widget.listUpdated()




if __name__ == '__main__':
    def exit(w=None, data=None):
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

    widget = Localed(rootdir)
    mainWindow = gtk.Window()
    mainWindow.connect("destroy", exit)
    mainWindow.set_border_width(3)
    mainWindow.add(widget)
    widget.revert_cb()
    mainWindow.show_all()
    gtk.main()

