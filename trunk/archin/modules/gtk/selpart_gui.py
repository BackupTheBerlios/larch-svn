# selpart_gui.py - extra widgets for the manual partition selection stage
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
# 2008.01.28

import gtk

class SelTable(gtk.ScrolledWindow):
    """This widget presents a list of available partitions for
    allocation in the new system.
    """
    def __init__(self, master, filesystems, mountpoints):
        self.master = master
        self.mountpoints = mountpoints
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.table = gtk.Table(2, 6)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)
        self.add_with_viewport(self.table)
        self.rows = []
        # column headers
        i = 0
        for l in (_(" Partition "), _("Mount Point"), _("   Size   "),
                _("Format"), _("File-system"), _("Options")):
            lw = gtk.Button(l)
            self.table.attach(lw, i, i+1, 0, 1, yoptions=0)
            i += 1

        line = gtk.HSeparator()
        self.table.attach(line, 0, 6, 1, 2, yoptions=0)

        #self.mp_liststore = gtk.ListStore(str)
        #for mp in mountpoints:
        #    self.mp_liststore.append([mp])
        # Note: it might be better to have an individual list for each
        # partition, so that (a) /mnt/% can be substituted, and (b) the
        # already allocated mount points can be left out.

        self.filesystems = filesystems
        self.fs_liststore = gtk.ListStore(str)
        self.cellr = gtk.CellRendererText()
        for fs in filesystems:
            self.fs_liststore.append([fs])

    def renew(self, partlist):
        # First remove old widgets
        for r in self.rows:
            # The first item in each row list is the Partition instance,
            # the remaining items are the widgets
            for w in r[1:]:
                self.table.remove(w)
        self.rows = []

        self.table.resize(len(partlist) + 2, 6)
        ri = 1
        for p in partlist:
            devw = gtk.Label(p.partition)


            #mpw = gtk.combo_box_entry_new_text()
            mpw = SelMountPoint(self, p, self.mountpoints)


            #set to p.mountpoint)


            try: s = "%8.1f GB" % float(p.size) / 1000
            except: s = '?'
            sizew = gtk.Label(s)
            fmtw = gtk.CheckButton()
            fmtw.set_active(p.format)
            fmtw.connect("toggled", self.fmtw_cb, p)
            fstw = gtk.ComboBox(self.fs_liststore)
            fstw.pack_start(self.cellr, True)
            fstw.add_attribute(self.cellr, 'text', 0)
            fs = p.newformat or p.existing_format
            try:
                fstw.set_active(self.filesystems.index(fs))
            except:
                if (fs == None):
                    fstw.set_active(-1)
                else:
                    raise

            fstw.set_sensitive(p.format)
            # callable externally as:
            #self.enable_fstype(p, p.format)

            fstw.connect("changed", self.fstw_cb, p)


            optw = gtk.Button()
            optw.connect("clicked", self.popupOptions, p)

            ri += 1
            self.table.attach(devw, 0, 1, ri, ri+1, yoptions=0)
            self.table.attach(mpw, 1, 2, ri, ri+1, yoptions=0)
            self.table.attach(sizew, 2, 3, ri, ri+1, yoptions=0)
            self.table.attach(fmtw, 3, 4, ri, ri+1, xoptions=0, yoptions=0)
            self.table.attach(fstw, 4, 5, ri, ri+1, yoptions=0)
            self.table.attach(optw, 5, 6, ri, ri+1, yoptions=0)
            self.rows.append([p, devw, mpw, sizew, fmtw, fstw, optw])

            self.fstw_cb(fstw, p)
            #self.update_options(p)

    def popupOptions(self, widget, partition):
        self.popup_part = partition
        fo = partition.get_format_options()
        mo = partition.get_mount_options()
        rows = []
        if fo:
            rows.append(gtk.HSeparator())
            fl = gtk.Label()
            fl.set_markup("<b>%s</b>" % _("Formatting options"))
            fl.set_alignment(0.0, 0.5)
            rows.append(fl)
            rows.append(gtk.HSeparator())
            for opt in fo:
                rows.append(self.newOption(opt))
            if mo:
                rows.append(gtk.HSeparator())

        if mo:
            rows.append(gtk.HSeparator())
            ml = gtk.Label()
            ml.set_markup("<b>%s</b>" % _("Mount options"))
            ml.set_alignment(0.0, 0.5)
            rows.append(ml)
            rows.append(gtk.HSeparator())
            for opt in mo:
                rows.append(self.newOption(opt))

        if not rows:
            return
        dlg = gtk.Dialog(_("Options for %s") % partition.partition, None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_OK, gtk.RESPONSE_OK))

        table = gtk.Table(len(rows), 2)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        dlg.vbox.pack_start(table)
        i = 0
        for r in rows:
            if isinstance(r, tuple):
                table.attach(r[0], 0, 1, i, i+1, xoptions=gtk.FILL)
                table.attach(r[1], 1, 2, i, i+1, xoptions=gtk.EXPAND|gtk.FILL)
            else:
                table.attach(r, 0, 2, i, i+1)
            i += 1

        dlg.vbox.show_all()
        dlg.run()
        dlg.destroy()
        self.update_options(partition)

    def update_options(self, p):
        for r in self.rows:
            if (p == r[0]):
                break
        fo = p.format_options
        if not fo:
            fo = ''
        mo = p.mount_options
        if not mo:
            mo = ''
        r[6].set_label("%s - %s" % (fo, mo))

    def newOption(self, opt):
        cb = gtk.CheckButton(opt[0])
        cb.set_active(opt[2])
        cb.connect("toggled", self.opt_cb, opt[1])
        hf = gtk.Frame()
        hl = gtk.Label(opt[3])
        hl.set_line_wrap(True)
        hl.set_size_request(400, -1)
        hf.add(hl)
        return (cb, hf)

    def opt_cb(self, widget, flag):
        if flag.isupper():
            self.popup_part.mount_options_cb(flag, widget.get_active())
        else:
            self.popup_part.format_options_cb(flag, widget.get_active())

    def fstw_cb(self, widget, part):
        part.fstype_cb(self, widget.get_active_text())
        self.update_options(part)

    def fmtw_cb(self, widget, part):
        part.format_cb(self, widget.get_active())

    def enable_fstype(self, part, on):
        for r in self.rows:
            if (part == r[0]):
                r[5].set_sensitive(on)

    def enable_mountpoint(self, part, on):
        for r in self.rows:
            if (part == r[0]):
                r[2].set_sensitive(on)

    def set_mountpoint(self, part, mp):
        if not mp:
            mp = ''
        for r in self.rows:
            if (part == r[0]):
                r[2].set_text(mp)

    def mountpoint_text_cb(self, widget, part):
        part.mountpoint_cb(widget.get_text())
        self.update_options(part)

    def set_fstype(self, part, fst):
        for r in self.rows:
            if (part == r[0]):
                break

        try:
            r[5].set_active(self.filesystems.index(fst))
        except:
            if (fst == None):
                r[5].set_active(-1)
            else:
                raise


class SelDevice(gtk.HBox):
    """This widget allows selection of the device on which partitions are
    to be allocated to mountpoints, formatted, etc.
    """
    def __init__(self, master, devices):
        gtk.HBox.__init__(self)
        self.master = master
        label = gtk.Label(_("Configuring partitions on drive "))
        combo = gtk.combo_box_new_text()
        for d in devices:
            combo.append_text(d.rstrip('-'))
        combo.connect('changed', self.newdevice)

    def newdevice(self, widget, data=None):
        self.master.setDevice(widget.get_active_text())


class SelMountPoint(gtk.HBox):
    def __init__(self, table, part, mountpoints):
        self.mountpoints = mountpoints
        gtk.HBox.__init__(self)
        self.en = gtk.Entry()
        self.en.set_width_chars(10)
        self.en.connect("changed", table.mountpoint_text_cb, part)
        pb = gtk.Button()
        pb.add(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE))
        pb.connect("clicked", self.pb_cb, part)
        pb.connect("button_press_event", self.pb_cb, part)
        self.pack_start(self.en)
        self.pack_start(pb)
        self.show_all()

    def pb_cb(self, widget, event, part):
        if (event.type != gtk.gdk.BUTTON_PRESS):
            # We have not handled this event, pass it on
            return False

        menu = gtk.Menu()
        mplist = []
        for p in install.parts.values():
            if p.mountpoint:
                mplist.append(p.mountpoint)

        for i in self.mountpoints:
            if (i in mplist):
                continue

            # Create a new menu-item
            menu_item = gtk.MenuItem(i)
            # ...and add it to the menu
            menu.append(menu_item)
            menu_item.connect("activate", self.menuitem_cb, i)
            menu_item.show()
        menu.popup(None, None, None, event.button, event.time)

        # We have handled this event, don't pass it on
        return True

    def menuitem_cb(self, widget, item):
        self.en.set_text(item)

    def set_text(self, text):
        self.en.set_text(text)