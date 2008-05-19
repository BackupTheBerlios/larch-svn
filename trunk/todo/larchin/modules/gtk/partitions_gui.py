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
# 2008.05.19

import gtk


class SwapWidget(gtk.Frame):
    """This widget allows a swap partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, size_cb):
        gtk.Frame.__init__(self)
        self.size_callback = size_cb
        adjlabel = gtk.Label(_("Set size of swap partition (GB)"))
        adjlabel.set_alignment(0.9, 0.5)
        self.swapadj = gtk.Adjustment(lower=0.2, step_incr=0.1, page_incr=1.0)
        hscale = gtk.HScale(self.swapadj)

        self.swapon = gtk.CheckButton(_("Create swap partition"))

        self.set_label_widget(self.swapon)
        self.swapbox = gtk.VBox()
        self.swapbox.pack_start(adjlabel)
        self.swapbox.pack_start(hscale)

        self.notice = gtk.Label(_("No swap partition allocated.\n"
                "Unless you have more memory than you will ever need"
                " it is a good idea to set aside some disk space"
                " for a swap partition."))
        self.notice.set_line_wrap(True)

        self.add(self.swapbox)

        self.swapstate = False
        self.swapadj.connect("value_changed", self.swap_size_cb, size_cb)
        self.swapon.connect("toggled", self.swap_check_cb)

    def swap_size_cb(self, widget, data=None):
        self.size_callback(self.swapadj.value)

    def swap_check_cb(self, widget, data=None):
        self.set_swap(self.swapon.get_active(), False)

    def set_swap(self, on, update=True):
        if (on != self.swapstate):
            self.swapstate = on
        if on:
            widget = self.swapbox
            self.size_callback(self.swapadj.value)
        else:
            widget = self.notice
            self.size_callback(0.0)
        if update:
            self.swapon.set_active(on)
        else:
            child = self.get_child()
            if child:
                self.remove(child)
            self.add(widget)
            widget.show()

    def set_adjust(self, lower = None, upper = None, value = None):
        """Set the size adjustment slider. Any of lower limit, upper limit
        and size can be set independently.
        """
        if (lower != None):
            self.swapadj.lower = lower
        if (upper != None):
            self.swapadj.upper = upper
        if ((value != None)
                and (value >= self.swapadj.lower)
                and (value <= self.swapadj.upper)):
            self.swapadj.value = value


class HomeWidget(gtk.Frame):
    """This widget allows a separate /home partition to be created.
    This function is just the constructor, the logic is handled by
    other functions.
    """
    def __init__(self, size_cb):
        gtk.Frame.__init__(self)
        self.size_callback = size_cb
        adjlabel = gtk.Label(_("Set size of '/home' partition (GB)"))
        adjlabel.set_alignment(0.9, 0.5)
        self.homeadj = gtk.Adjustment(lower=0.1, step_incr=0.1, page_incr=1.0)
        hscale = gtk.HScale(self.homeadj)

        self.homeon = gtk.CheckButton(_("Create '/home' partition"))

        self.set_label_widget(self.homeon)
        self.homebox = gtk.VBox()
        self.homebox.pack_start(adjlabel)
        self.homebox.pack_start(hscale)

        self.notice = gtk.Label(_("The creation of a separate partition"
                " for user data (in the folder /home) allows you to keep"
                " this separate from the system files.\n"
                "One advantage is that the operating system can later be"
                " freshly installed without destroying your data."))
        self.notice.set_line_wrap(True)

        self.add(self.homebox)

        self.is_enabled = False
        self.homestate = False
        self.homeadj.connect("value_changed", self.home_size_cb, size_cb)
        self.homeon.connect("toggled", self.home_check_cb)

    def home_size_cb(self, widget, data=None):
        self.size_callback(self.homeadj.value)

    def home_check_cb(self, widget, data=None):
        self.set_home(self.homeon.get_active(), False)

    def set_home(self, on, update=True):
        if (on != self.homestate):
            self.homestate = on
        if on:
            widget = self.homebox
            self.size_callback(self.homeadj.value)
        else:
            widget = self.notice
            self.size_callback(0.0)
        if update:
            self.homeon.set_active(on)
        else:
            child = self.get_child()
            if child:
                self.remove(child)
            self.add(widget)
            widget.show()

    def set_adjust(self, lower = None, upper = None,
            value = None, update = True):
        """Set the size adjustment slider. Any of lower limit, upper limit
        and size can be set independently.
        """
        if (lower != None):
            self.homeadj.lower = lower
        if (upper != None):
            self.homeadj.upper = upper
        if ((value != None)
                and (value >= self.homeadj.lower)
                and (value <= self.homeadj.upper)):
            self.homeadj.value = value

