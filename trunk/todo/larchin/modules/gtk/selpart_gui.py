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
# 2008.05.29

import gtk

class SelTable(gtk.ScrolledWindow):
    """This widget presents a list of available partitions for
    allocation in the new system.
    """
    def __init__(self, filesystems, mountpoints):
        self.mountpoints = mountpoints
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.table = gtk.Table(2, 7)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)
        self.add_with_viewport(self.table)
        self.rows = []
        # column headers
        i = 0
        for l in (_(" Partition "), _("Mount Point"), _("   Size   "),
                _("Mount Options"), _("Format"), _("File-system"),
                _("Format Options")):
            lw = gtk.Button(l)
            self.table.attach(lw, i, i+1, 0, 1, yoptions=0)
            i += 1

        line = gtk.HSeparator()
        self.table.attach(line, 0, 7, 1, 2, yoptions=0)

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

        ri = 1
        if partlist:
            self.table.resize(len(partlist) + ri+1, 7)
        else:
            self.table.resize(ri+2, 7)
            notice = gtk.Label(_("No partitions available on this device"))
            self.table.attach(notice, 0, 7, ri+1, ri+2, yoptions=0)
            self.rows = [[None, notice]]

        for p in partlist:
            # p is the information for a single partition
            devw = gtk.Label(p.partition)
            mpw = SelMountPoint(self, p, self.mountpoints)
            sizew = gtk.Label("%8.1f GB" % (float(p.size) / 1e9))
            fmtw = gtk.CheckButton()
            do_format = (p.newformat != "")
            fmtw.set_active(do_format)
            fmtw.connect("toggled", self.fmtw_cb, p)
            fstw = gtk.ComboBox(self.fs_liststore)
            fstw.pack_start(self.cellr, True)
            fstw.add_attribute(self.cellr, 'text', 0)
            try:
                fstw.set_active(self.filesystems.index(p.newformat))
            except:
                fstw.set_active(-1)

            fstw.set_sensitive(do_format)

            fstw.connect("changed", self.fstw_cb, p)

            moptw = gtk.Button()
            moptw.connect("clicked", self.popupMountOptions, p)

            foptw = gtk.Button()
            foptw.connect("clicked", self.popupFormatOptions, p)

            ri += 1
            self.table.attach(devw, 0, 1, ri, ri+1, yoptions=0)
            self.table.attach(mpw, 1, 2, ri, ri+1, yoptions=0)
            self.table.attach(sizew, 2, 3, ri, ri+1, yoptions=0)
            self.table.attach(moptw, 3, 4, ri, ri+1, yoptions=0)
            self.table.attach(fmtw, 4, 5, ri, ri+1, xoptions=0, yoptions=0)
            self.table.attach(fstw, 5, 6, ri, ri+1, yoptions=0)
            self.table.attach(foptw, 6, 7, ri, ri+1, yoptions=0)
            self.rows.append([p, devw, mpw, sizew, moptw, fmtw, fstw, foptw])

            self.fstw_cb(fstw, p)

        self.table.show_all()

    def popupMountOptions(self, widget, partdata):
        mo = partdata.get_mount_options()
        rows = []
        if mo:
            for opt in mo:
                rows.append(self.newOption(opt))

        if not rows:
            return
        dlg = gtk.Dialog(_("Mount Options for %s, mounted at %s") %
                (partdata[0], partdata[1]), None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_OK, gtk.RESPONSE_OK))

        table = gtk.Table(len(rows), 2)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        dlg.vbox.pack_start(table)
        i = 0
        for r in rows:
            table.attach(r[0], 0, 1, i, i+1, xoptions=gtk.FILL)
            table.attach(r[1], 1, 2, i, i+1, xoptions=gtk.EXPAND|gtk.FILL)
            i += 1

        dlg.vbox.show_all()
        dlg.run()
        dlg.destroy()
        i = 0
        mflags = ""
        for r in rows:
            f = mo[i][1]
            if r[0].get_active():
                f = f.upper()
            mflags += f
        partdata.set_mount_flags(mflags)
        widget.set_label(mflags)

    def popupFormatOptions(self, widget, partdata):
        fo = partdata.get_fprmat_options()
        rows = []
        if fo:
            for opt in fo:
                rows.append(self.newOption(opt))

        if not rows:
            return
        dlg = gtk.Dialog(_("Formatting Options for %s") %
                partdata[0], None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_OK, gtk.RESPONSE_OK))

        table = gtk.Table(len(rows), 2)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        dlg.vbox.pack_start(table)
        i = 0
        for r in rows:
            table.attach(r[0], 0, 1, i, i+1, xoptions=gtk.FILL)
            table.attach(r[1], 1, 2, i, i+1, xoptions=gtk.EXPAND|gtk.FILL)
            i += 1

        dlg.vbox.show_all()
        dlg.run()
        dlg.destroy()
        i = 0
        fflags = ""
        for r in rows:
            f = fo[i][1]
            if r[0].get_active():
                f = f.upper()
            fflags += f
        partdata.set_format_flags(fflags)
        widget.set_label(fflags)



        self.popup_part = partdata
        fo = partition.get_format_options(partdata[4])
        mo = partition.get_mount_options(partdata[4])
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
        hf = gtk.Frame()
        hl = gtk.Label(opt[3])
        hl.set_line_wrap(True)
        hl.set_size_request(400, -1)
        hf.add(hl)
        return (cb, hf)

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
            r[5].set_active(-1)


class SelDevice(gtk.Frame):
    """This widget allows selection of the device on which partitions are
    to be allocated to mountpoints, formatted, etc.
    """
    def __init__(self, devices, setdev_cb):
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        hb = gtk.HBox()
        self.setdev_cb = setdev_cb
        self.devices = devices
        label = gtk.Label(_("Configuring partitions on drive "))
        hb.pack_start(label, False)
        self.combo = gtk.combo_box_new_text()
        hb.pack_start(self.combo, False)
        self.add(hb)
        for d in devices:
            self.combo.append_text(d)
        self.combo.connect('changed', mainWindow.sigprocess, self.newdevice)
        # Ensure first device is selected and initialized
        self.combo.set_active(-1)
        self.combo.set_active(0)

    def newdevice(self, data):
        d = self.combo.get_active_text()
        self.updated = True
        if d:
            self.setdev_cb(d)


class SelMountPoint(gtk.HBox):
    def __init__(self, table, part, mountpoints):
        self.mountpoints = mountpoints
        gtk.HBox.__init__(self)
        self.en = gtk.Entry()
        self.en.set_width_chars(10)
        if part.mountpoint:
            self.en.set_text(part.mountpoint)
        self.en.connect("changed", table.mountpoint_text_cb, part)
        pb = gtk.Button()
        pb.add(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE))
        pb.connect("clicked", self.pb_cb, part)
        pb.connect("button_press_event", self.pb_cb, part)
        self.pack_start(self.en)
        self.pack_start(pb)
#        self.show_all()

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
