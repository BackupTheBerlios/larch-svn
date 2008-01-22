# partauto.py - automatic partitioning stage
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
# 2008.01.20

class AutoPart(Stage, gtk.VBox):
    def stageTitle(self):
        return _("Installation partitions")

    def getHelp(self):
        return _("The available space will be divided into two or three"
                " partitions. If there is sufficient space a separate home"
                " partition will be created (optionally), to keep user"
                " data separate from system data and programs. This can be"
                " helpful when updating or changing the operating system.\n\n"
                "Also, a 'swap' partition will be created as a"
                " buffer area for situations in which more memory than the"
                " computer actually has is needed - system crashes are thus"
                " avoided, although processing speed will probably be"
                " seriously impaired in such a situation.\n\n"
                "If you need finer control over the use of your disk space"
                " you must use the 'custom partitioning' option.")

    def __init__(self):
        gtk.VBox.__init__(self)
        self.reinit()

    def reinit(self):
        MINSPLITSIZE = 20.0    # GB
        SWAPSIZE = 1.0         # GB
        HOMESIZE = 50          # % of total
        Stage.__init__(self)
        install.clearParts()

        dev = install.selectedDevice()
        # Info on drive and partitions (dev="/dev/sda", etc.):
        install.getDeviceInfo(dev)
        self.linuxspace = float(install.dsize) / 1000
        self.addLabel(_("Total capacity of drive %s: %6.1f GB") %
                (dev, install.dsize))
        if (install.autoPartStart == 1):
            self.linuxspace -= (float(install.p1end) / 1000)
        self.addLabel(_("Space available for Arch Linux: %6.1f GB") %
                self.linuxspace)

        # root partition size
        root = gtk.HBox()
        l = gtk.Label(_("Size of root ('/') partition (GB):"))
        self.rootsizew = gtk.Entry()
        self.rootsizew.set_editable(False)
        root.pack_start(l)
        root.pack_end(self.rootsizew)
        self.addWidget(root)

        # swap partition size
        swap = gtk.HBox()
        l = gtk.Label(_("Size of swap partition (GB):"))
        upper = float(self.linuxspace) / 20
        if (upper > 4.0):
            upper = 4.0
        elif (upper < SWAPSIZE):
            upper = SWAPSIZE
        adj = gtk.Adjustment(value=SWAPSIZE, lower=0.0, upper=upper,
                step_incr=0.1, page_incr=0.5)
        self.swapsizew = gtk.SpinButton(adj, digits=1)
        self.swapsizew.set_numeric(True)
        self.swapsizew.set_snap_to_ticks(True)
        self.swapsizew.set_wrap(False)
        self.swapsizew.set_update_policy(gtk.UPDATE_IF_VALID)
        swap.pack_start(l)
        swap.pack_end(self.swapsizew)
        self.swapsizew.connect('value-changed', self.size_changed)
        self.addWidget(swap)

        if (self.linuxspace >= MINSPLITSIZE):
            # Offer option with /home, preactivated.
            # Including slider for adjusting split.
            homedef = self.linuxspace * HOMESIZE / 100
            homemin = 5.0
            homemax = self.linuxspace - 5.0 - upper

            self.home = gtk.Frame()
            adjlabel = gtk.Label(_("Set size of /home partition (GB)"))
            self.homeadj = gtk.Adjustment(homedef, homemin, homemax,
                    step_incr=0.1, page_incr=1.0)
            hscale = gtk.HScale(self.homeadj)
            self.homeadj.connect("value_changed", self.home_value_cb)
            self.home.add(hscale)
            self.addWidget(self.home)

            self.homebut = gtk.CheckButton(
                    _("Create separate '/home' partition"))
            self.home.set_label_widget(self.homebut)
            self.homebut.connect("toggled", self.home_check_cb)
            self.homebut.set_active(False)
            self.homebut.set_active(True)

        # Offer automatic partitioning
        self.addOption('auto', _("Automatic partitioning (as above)"), True)

        # Offer manual partitioning
        self.addOption('custom', _("Custom partitioning"))

    def home_check_cb(self, widget, data=None):
        on = widget.get_active()
        self.home.set_sensitive(on)
        if on:
            self.home_value_cb(widget)
        else:
            self.homesize = 0
            self.size_changed(widget)

    def home_value_cb(self, widget, data=None):
        self.homesize = self.homeadj.get_value()
        self.size_changed(widget)

    def size_changed(self, widget, data=None):
        """After a change in self.homesize, or the swap size, update
        self.rootsize and it's display.
        """
        self.rootsize = (self.linuxsize - self.homesize -
                self.swapsizew.get_value())
        self.rootsizew.set_value(self.rootsize)


    def forward(self):
        sel = self.getSelectedOption()
        if (sel == 'custom'):
            mainWindow.goto('manualPart')
            return

#?
        endmark = install.dsize #-1?
        if install.autoPartStart:
            # keep 1st partition, allocate from 2nd
            startmark = install.p1end
            partno = 2
        else:
            startmark = 0
            partno = 1

# Tricky logic here! The first partition should be root, then swap then
# home, but swap and/or home may be absent. The last partition should take
# its endpoint from 'endmark', root's start from startmark. The actual
# partitioning should be done, but the formatting can be handled - given
# the appropriate information - by the installation stage.

        # Remove all existing partitions (except optionally the first)
        install.rmparts(dev, partno)

        swapsize = self.swapsizew.get_value()
        if (self.homesize == 0) and (swapsize == 0):
            em = endmark
        else:
            em = startmark + int(self.rootsize * 1000)
        install.mkpart(partno, startmark, em)
        startmark = em
        install.defpart(dev, partno, '/')

        if (swapsize != 0):
            partno += 1
            if (self.homesize == 0):
                em = endmark
            else:
                em = startmark + int(swapsize * 1000)
            install.mkpart(dev, partno, startmark, em, 'linux-swap')
            startmark = em

        if self.homesize:
            partno += 1
            install.mkpart(partno, startmark, endmark)
            install.defpart(dev, partno, '/home')

        mainWindow.goto('install')


stages['autoPart'] = AutoPart
