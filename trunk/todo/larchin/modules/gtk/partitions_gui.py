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
# 2008.05.13

import gtk


class SwapWidget(gtk.Frame):
    """This widget allows a swap partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        self.master = master
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
        self.swapstate = False
        self.size = 0.0
        self.swapadj.connect("value_changed", self.swap_size_cb)
        self.swapon.connect("toggled", self.swap_check_cb)

    def enable(self, on):
        """Show (on=True) or hide (on=False) the swap partition widget.
        """
        if on:
            self.show()
            # Make having a swap partition the default
            self.set_swap(True)
        else:
            self.hide()
        self.is_enabled = on

    def swap_size_cb(self, widget, data=None):
        self.set_adjust(value=self.swapadj.value, update=False)

    def swap_check_cb(self, widget, data=None):
        self.set_swap(self.swapon.get_active(), False)

    def set_swap(self, on, update=True):
        if (on != self.swapstate):
            self.swapstate = on
            self.master.swapsize_cb()
        if on:
            self.swapbox.show()
        else:
            self.swapbox.hide()
        if update:
            self.swapon.set_active(on)

    def set_adjust(self, lower = None, upper = None,
            value = None, update = True):
        """Set the size adjustment slider. Any of lower limit, upper limit
        and size can be set independently.
        """
        osize = self.size
        if (lower != None):
            self.swapadj.lower = lower
            if (self.size < lower):
                self.size = lower
                self.swapadj.value = lower
        if (upper != None):
            self.swapadj.upper = upper
            if (self.size > upper):
                self.size = upper
                self.swapadj.value = upper
        if ((value != None) and (value != self.size)
                and (value >= self.swapadj.lower)
                and (value <= self.swapadj.upper)):
            self.size = value
            if update:
                self.swapadj.value = value

        if (osize != self.size):
            self.master.swapsize_cb()


class HomeWidget(gtk.Frame):
    """This widget allows a separate /home partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, master):
        gtk.Frame.__init__(self)
        self.master = master
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
        self.homestate = False
        self.size = 0.0
        self.homeadj.connect("value_changed", self.home_size_cb)
        self.homeon.connect("toggled", self.home_check_cb)

    def enable(self, on):
        """Show (on=True) or hide (on=False) the home partition widget.
        """
        if on:
            self.show()
            # Make having a home partition the default
            self.set_home(True)
        else:
            self.hide()
        self.is_enabled = on

    def home_size_cb(self, widget, data=None):
        self.set_adjust(value=self.homeadj.value, update=False)

    def home_check_cb(self, widget, data=None):
        self.set_home(self.homeon.get_active(), False)

    def set_home(self, on, update=True):
        if (on != self.homestate):
            self.homestate = on
            self.master.homesize_cb()
        if on:
            self.homebox.show()
        else:
            self.homebox.hide()
        if update:
            self.homeon.set_active(on)

    def set_adjust(self, lower = None, upper = None,
            value = None, update = True):
        """Set the size adjustment slider. Any of lower limit, upper limit
        and size can be set independently.
        """
        osize = self.size
        if (lower != None):
            self.homeadj.lower = lower
            if (self.size < lower):
                self.size = lower
                self.homeadj.value = lower
        if (upper != None):
            self.homeadj.upper = upper
            if (self.size > upper):
                self.size = upper
                self.homeadj.value = upper
        if ((value != None) and (value != self.size)
                and (value >= self.homeadj.lower)
                and (value <= self.homeadj.upper)):
            self.size = value
            if update:
                self.homeadj.value = value

        if (osize != self.size):
            self.master.homesize_cb()


class RootWidget(gtk.HBox):
    """A widget to display (only - it is not editable) the space
    available for the Linux root ('/') partition when using automatic
    partitioning. When using manual partitioning it shows the total
    amount of space available for Linux.
    """
    def __init__(self):
        gtk.HBox.__init__(self)
        rootlabel = gtk.Label(_("Space for Linux system (GB):  "))
        self.rootsizew = gtk.Entry(10)
        self.rootsizew.set_editable(False)
        self.pack_end(self.rootsizew, False)
        self.pack_end(rootlabel, False)

    def set_value(self, flval):
        self.rootsizew.set_text("%8.1f" % flval)

