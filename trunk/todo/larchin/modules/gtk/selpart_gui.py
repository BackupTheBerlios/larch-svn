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
# 2008.05.31

import gtk

class SelTable(gtk.ScrolledWindow):
    """This widget presents a list of available partitions for
    allocation in the new system.
    """
    def __init__(self, master):
        self.master = master
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.table = gtk.Table(2, 7)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)
        self.add_with_viewport(self.table)
        self.partlist = []
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

        self.fs_liststore = gtk.ListStore(str)
        self.cellr = gtk.CellRendererText()
        for fs in install.filesystems:
            self.fs_liststore.append([fs])

    def clear(self):
        """Clear the partition table in preparation for switching to
        another disk drive.
        """
        # Remove old widgets
        for p in self.partlist:
            self.table.remove(p.devw)
            self.table.remove(p.mpw)
            self.table.remove(p.sizew)
            self.table.remove(p.moptw)
            self.table.remove(p.fmtw)
            self.table.remove(p.fstw)
            self.table.remove(p.foptw)
        # Forget the previous partitions
        self.partlist = []

    def addrow(self, partobj):
        """Add a row to the table corresponding to the partition object
        passed as argument.
        """
        ri = len(self.partlist) + 2
        self.partlist.append(partobj)
        self.table.resize(ri+1, 7)
        self.table.attach(partobj.devw, 0, 1, ri, ri+1, yoptions=0)
        self.table.attach(partobj.mpw, 1, 2, ri, ri+1, yoptions=0)
        self.table.attach(partobj.sizew, 2, 3, ri, ri+1, yoptions=0)
        self.table.attach(partobj.moptw, 3, 4, ri, ri+1, yoptions=0)
        self.table.attach(partobj.fmtw, 4, 5, ri, ri+1, xoptions=0, yoptions=0)
        self.table.attach(partobj.fstw, 5, 6, ri, ri+1, yoptions=0)
        self.table.attach(partobj.foptw, 6, 7, ri, ri+1, yoptions=0)

        partobj.fstw.set_model(self.fs_liststore)
        partobj.fstw.pack_start(self.cellr, True)
        partobj.fstw.add_attribute(self.cellr, 'text', 0)
        try:
            partobj.fstw.set_active(install.filesystems.index(
                    partobj.newformat))
        except:
            partobj.fstw.set_active(-1)

    def showtable(self):
        """To be called when the partition table has been completed.
        """
        if not self.partlist:
            self.table.resize(3, 7)
            notice = gtk.Label(_("No partitions available on this device"))
            self.table.attach(notice, 0, 7, 2, 3, yoptions=0)

        self.table.show_all()







class SelDevice(gtk.Frame):
    """This widget allows selection of the device on which partitions are
    to be allocated to mountpoints, formatted, etc.
    """
    def __init__(self, devices, setdev_cb):
        self.setdev_cb = setdev_cb
        self.devices = devices
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        hb = gtk.HBox()
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
    def __init__(self, partobj):
        self.partobj = partobj
        gtk.HBox.__init__(self)
        self.en = gtk.Entry()
        self.en.set_width_chars(15)
        if partobj.mountpoint:
            self.en.set_text(partobj.mountpoint)
        self.en.connect("changed", partobj.mountpoint_text_cb)
        pb = gtk.Button()
        pb.add(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE))


        # Why the two connections?
        #pb.connect("clicked", self.pb_cb)
        pb.connect("button_press_event", self.pb_cb)


        self.pack_start(self.en)
        self.pack_start(pb)
#        self.show_all()

    def pb_cb(self, widget, event, data=None):

        # Explain this!
        if (event.type != gtk.gdk.BUTTON_PRESS):
            # We have not handled this event, pass it on
            return False

        menu = gtk.Menu()

        # Get list of used mountpoints
        mplist = self.partobj.get_used_mountpoints()

        # Exclude these from the default list of suggestions
        for i in install.mountpoints:
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


class PartitionGui:
    """This class is used as the base class for the Partition class,
    providing the associated gui functions.
    """
    def __init__(self):
        self.devw = gtk.Label(self.partition)

        self.mpw = SelMountPoint(self)

        self.sizew = gtk.Label("%8.1f GB" % (float(self.size) / 1e9))

        self.fmtw = gtk.CheckButton()
        do_format = (self.newformat != "")
        self.fmtw.set_active(do_format)
        self.fmtw.connect("toggled", self.fmtw_cb)
        self.fstw = gtk.ComboBox()

        self.fstw.set_sensitive(do_format)
        self.fstw.connect("changed", self.fstw_cb)

        self.moptw = gtk.Button()
        self.moptw.connect("clicked", self.popupMountOptions)

        self.foptw = gtk.Button()
        self.foptw.connect("clicked", self.popupFormatOptions)


        # ???
        self.fstw_cb()

    def popupMountOptions(self, widget, data=None):
        mo = self.get_mount_options()
        rows = []
        if mo:
            for opt in mo:
                rows.append(self.newOption(opt))

        if not rows:
            return
        dlg = gtk.Dialog(_("Mount Options for %s, mounted at %s") %
                (self.partition, self.mountpoint), None,
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
            i += 1
        self.set_mount_flags(mflags)
        widget.set_label(mflags)

    def popupFormatOptions(self, widget, data=None):
        fo = self.get_format_options()
        rows = []
        if fo:
            for opt in fo:
                rows.append(self.newOption(opt))

        if not rows:
            return
        dlg = gtk.Dialog(_("Formatting Options for %s") %
                self.partition, None,
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
            i += 1
        self.set_format_flags(fflags)
        widget.set_label(fflags)

    def newOption(self, opt):
        cb = gtk.CheckButton(opt[0])
        cb.set_active(opt[2])
        hf = gtk.Frame()
        hl = gtk.Label(opt[3])
        hl.set_line_wrap(True)
        hl.set_size_request(400, -1)
        hf.add(hl)
        return (cb, hf)

    def fmtw_cb(self, widget, data=None):
        on = widget.get_active()
        if on:
            # If activating formatting, set the fstype to the default
            fstype = "ext3"
            fsformat = fstype
        else:
            # otherwise set the fstype to the existing one (if any) and
            # disable the combobox
            fstype = self.existing_format
            fsformat = ""
        self.set_fstype(fstype, on)
        part.format_cb(fsformat)
        # Now reset the labels on the option buttons
        self.set_mount_options(part)
        self.set_format_options(part)

    def set_fstype(self, fst, enable=True):
        try:
            self.fstw.set_active(install.filesystems.index(fst))
        except:
            self.fstw.set_active(-1)

        self.fstw.set_sensitive(enable)

    def set_mount_options(self):
        self.moptw.set_label(self.mount_options)

    def set_format_options(self):
        self.foptw.set_label(self.format_options)

    def fstw_cb(self, widget, data=None):
        self.format_cb(widget.get_active_text())
        # Now reset the labels on the option buttons
        self.set_mount_options()
        self.set_format_options()

    def mountpoint_text_cb(self, widget, data=None):
        self.mountpoint_cb(widget.get_text())
        self.set_mount_options()




    def format_cb(self, table, on):
        self.format = on
        table.enable_fstype(self, on)
        table.enable_mountpoint(self, on)
        # Ensure changed signal emitted when real setting passed (later)
        table.set_fstype(self, None)
        if on:
            newfs = self.existing_format
            if not newfs:
                newfs = 'ext3'
            table.set_fstype(self, newfs)

        else:
            self.newformat = None
            if not self.mountpoint:
                self.mount_options = None
