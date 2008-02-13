# partitions_gui.py - extra widgets for the partitions stage
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
# 2008.01.23

import gtk

class NtfsWidget(gtk.Frame):
    """This widget allows an existing operating system (Windows/NTFS)
    to be retained (optionally). It also provides for shrinking the
    partition used by that operating system. This function is just the
    constructor, the logic is handled by other functions.
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        adjlabel = gtk.Label(_("Set new size of NTFS partition (GB)"))
        adjlabel.set_alignment(0.9, 0.5)
        self.ntfsadj = gtk.Adjustment(step_incr=0.1, page_incr=1.0)
        hscale = gtk.HScale(self.ntfsadj)

        self.shrink = gtk.CheckButton(_("Shrink NTFS partition"))

        self.ntfsframe = gtk.Frame()
        self.ntfsframe.set_border_width(10)
        self.ntfsframe.set_label_widget(self.shrink)
        self.ntfsbox = gtk.VBox()
        self.ntfsbox.pack_start(adjlabel)
        self.ntfsbox.pack_start(hscale)
        self.ntfsframe.add(self.ntfsbox)

        self.keep1 = gtk.CheckButton(_("Retain existing operating system"
                " on first partition"))

        vbox = gtk.VBox()
        vbox.pack_start(self.keep1)
        vbox.pack_start(self.ntfsframe)
        self.add(vbox)

        self.ntfsadj.connect("value_changed", self.ntfs_size_cb, master)
        self.shrink.connect("toggled", self.shrink_check_cb, master)
        self.keep1.connect("toggled", self.keep1_check_cb, master)

    def enable(self, on):
        self.set_keep1(not on)
        self.set_keep1(on)
        self.set_sensitive(on)
        self.is_enabled = on

    def isenabled(self):
        return self.is_enabled

    def keep1_check_cb(self, widget, master):
        master.keep1_cb(widget.get_active())

    def shrink_check_cb(self, widget, master):
        master.shrink_cb(widget.get_active())

    def ntfs_size_cb(self, widget, master):
        master.ntfssize_cb(self.get_shrinkadjust())

    def get_shrink_on(self):
        return self.shrink.get_active()

    def set_shrink(self, on):
        self.shrink.set_active(on)

    def get_shrinkadjust(self):
        return float(self.ntfsadj.get_value())

    def set_shrinkadjust(self, lower = None, upper = None, value = None):
        if (lower != None):
            self.ntfsadj.lower = lower
        if (upper != None):
            self.ntfsadj.upper = upper
        if (value != None):
            self.ntfsadj.value = value

    def get_keep1_on(self):
        return self.keep1.get_active()

    def set_keep1(self, on):
        self.keep1.set_active(on)

    def enable_shrinkframe(self, on):
        self.ntfsframe.set_sensitive(on)

    def enable_shrinkswitch(self, on):
        self.shrink.set_sensitive(on)

    def enable_shrinkadjust(self, on):
        self.ntfsbox.set_sensitive(on)


class SwapWidget(gtk.Frame):
    """This widget allows a swap partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        adjlabel = gtk.Label(_("Set size of swap partition (GB)"))
        adjlabel.set_alignment(0.9, 0.5)
        self.swapadj = gtk.Adjustment(lower=0.2, step_incr=0.1, page_incr=1.0)
        hscale = gtk.HScale(self.swapadj)

        self.swapon = gtk.CheckButton(_("Create swap partition"))

        self.set_label_widget(self.swapon)
        self.swapbox = gtk.VBox()
        self.swapbox.pack_start(adjlabel)
        self.swapbox.pack_start(hscale)
        self.add(self.swapbox)

        self.is_enabled = False
        self.swapadj.connect("value_changed", self.swap_size_cb, master)
        self.swapon.connect("toggled", self.swap_check_cb, master)

    def enable(self, on):
        self.set_sensitive(on)
        self.is_enabled = on

    def isenabled(self):
        return self.is_enabled

    def set_on(self, on):
        self.swapon.set_active(on)

    def get_on(self):
        return self.swapon.get_active()

    def swap_size_cb(self, widget, master):
        master.swapsize_cb(self.get_value())

    def swap_check_cb(self, widget, master):
        master.swap_cb(widget.get_active())

    def get_value(self):
        return self.swapadj.value

    def enable_adjust(self, on):
        self.swapbox.set_sensitive(on)

    def set_adjust(self, lower = None, upper = None, value = None):
        if (lower != None):
            self.swapadj.lower = lower
        if (upper != None):
            self.swapadj.upper = upper
        if (value != None):
            self.swapadj.value = value


class HomeWidget(gtk.Frame):
    """This widget allows a separate /home partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        adjlabel = gtk.Label(_("Set size of '/home' partition (GB)"))
        adjlabel.set_alignment(0.9, 0.5)
        self.homeadj = gtk.Adjustment(lower=0.1, step_incr=0.1, page_incr=1.0)
        hscale = gtk.HScale(self.homeadj)

        self.homeon = gtk.CheckButton(_("Create '/home' partition"))

        self.set_label_widget(self.homeon)
        self.homebox = gtk.VBox()
        self.homebox.pack_start(adjlabel)
        self.homebox.pack_start(hscale)
        self.add(self.homebox)

        self.is_enabled = False
        self.homeadj.connect("value_changed", self.home_size_cb, master)
        self.homeon.connect("toggled", self.home_check_cb, master)

    def enable(self, on):
        self.set_sensitive(on)
        self.is_enabled = on

    def isenabled(self):
        return self.is_enabled

    def set_on(self, on):
        self.homeon.set_active(on)

    def get_on(self):
        return self.homeon.get_active()

    def home_size_cb(self, widget, master):
        master.homesize_cb(self.get_value())

    def home_check_cb(self, widget, master):
        master.home_cb(widget.get_active())

    def get_value(self):
        return self.homeadj.value

    def enable_adjust(self, on):
        self.homebox.set_sensitive(on)

    def set_adjust(self, lower = None, upper = None, value = None):
        if (lower != None):
            self.homeadj.lower = lower
        if (upper != None):
            self.homeadj.upper = upper
        if (value != None):
            self.homeadj.value = value


class RootWidget(gtk.HBox):
    """A widget to display (only - it is not editable) the space
    available for the Linux root ('/') partition when using automatic
    partitioning. When using manual partitioning it shows the total
    amount of space available for Linux.
    """
    def __init__(self, master):
        gtk.HBox.__init__(self)
        rootlabel = gtk.Label(_("Space for Linux system (GB):  "))
        self.rootsizew = gtk.Entry(10)
        self.rootsizew.set_editable(False)
        self.pack_end(self.rootsizew, False)
        self.pack_end(rootlabel, False)

    def set_value(self, flval):
        self.rootsizew.set_text("%8.1f" % flval)

