# partitions.py - Automatic partitioning and mount-point selection
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
# 2008.05.18

from stage import Stage, ShowInfoWidget
from partitions_gui import SwapWidget, HomeWidget
from dialogs import popupMessage

class Widget(Stage):
    def getHelp(self):
        return _("To make straightforward installations easier it is"
                " possible to choose a simple automatic division of your"
                " disk drive for the Arch Linux installation.\n\n"
                "WARNING: If you have an operating system already installed"
                " on this drive which you wish to keep, you must perform"
                " partitioning manually (or use the existing partitions) by"
                " selecting 'Manual Partitioning' (or 'Set Mount Points')"
                " from the stage menu.\n"
                "EXCEPTION: if the existing operating system uses the NTFS"
                " file-system (Windows), it is also possible to use automatic"
                " partitioning, if enough space is free, or has been freed"
                " by deleting or shrinking one or more NTFS partitions.\n\n"
                "Here only space after the last NTFS partition will be"
                " available for the new Linux installation. If you want to"
                " use some or all of the space occupied by Windows, you"
                " must shrink or remove the last NTS partitions first"
                " (by returning to the previous stage).")

    def __init__(self):
        Stage.__init__(self, moduleDescription)

        # Info on drive
        self.device = install.get_config('autodevice')
        self.dinfo = install.getDeviceInfo(self.device)

        # Info: total drive size
        totalsize = self.addWidget(ShowInfoWidget(
                _("Total capacity of drive %s:  ") % self.device))
        totalsize.set(self.dinfo[0])

        # Get partition info (consider only space after NTFS partitions)
        parts = install.getParts(self.device)
        self.startpart = 1
        self.startsector = 0
        for p in parts:
            if (p[1] == 'ntfs'):
                self.startpart = p[0] + 1
                self.startsector = p[4] + 1

        avsec = (self.dinfo[1] * self.dinfo[2] - self.startsector)
        self.avG = avsec * self.dinfo[3] / 1.0e9
        if (self.startpart > 1):
            popupMessage(_("One or more NTFS (Windows) partitions were"
                    " found. These will be retained. The available space"
                    " is thus reduced to %3.1f GB.\n"
                    "Allocation will begin at partition %d.") %
                        (self.avG, self.startpart))

        # swap size
        self.swap = self.addWidget(SwapWidget(self.swapsize_cb))

        # home size
        self.home = self.addWidget(HomeWidget(self.homesize_cb))

        # root size
        self.root = self.addWidget(ShowInfoWidget(
                _("Space for Linux system:  ")))

        # Clear list of assigned partitions
        install.clearParts()

#?

    def swapsize_cb(self, sizeG):
        self.swapsizeG = sizeG
        self.adjustroot()

    def homesize_cb(self, sizeG):
        self.homesizeG = sizeG
        self.adjustroot()

    def adjustroot(self):
        self.rootsizeG = self.avG - self.swapsizeG - self.homesizeG
        self.root.set("%8.1f GB" % self.rootsizeG)



#???
        MINSPLITSIZE = 20.0    # GB, if less available, no /home
        SWAPPZ0 = 5            # % of total, initial swap size???
        SWAPMAX  = 2.0         # GB, max swap size
        SWAPMAXPZ = 10         # % of total, max swap size
        SWAPDEF = 1.0          # GB, initial swap size???

        self.home_on = (self.avG >= MINSPLITSIZE)
        home_upper = self.avG - SWAPMAX - 5.0
        home_value = home_upper - 2.0
        self.home.set_adjust(upper=home_upper, value=home_value)
        self.home.enable(self.home_on and (not self.getCheck(self.expert)))

        swap_upper = freesize * SWAPMAXSIZE / 100
        if (swap_upper > SWAPMAX):
            swap_upper = SWAPMAX
        swap_value = freesize * SWAPSIZE / 100
        if (swap_value > SWAPDEF):
            swap_value = SWAPDEF
        self.swap.set_adjust(upper=swap_upper, value=swap_value)





    def forward(self):

        print "NYI"
        return 0

        # Set up the installation partitions automatically.
        if (self.ntfs.is_enabled and self.ntfs.keep1state):
            text = _(" * Wipe everything except the first partition")
            # allocate partitions from 2nd
            startmark = install.p1end       # altered by ntfsresize
            partno = 2
        else:
            text = _(" * Completely wipe the drive")
            startmark = 0
            partno = 1

        dev = install.selectedDevice()
        if not popupWarning(_("You are about to perform a destructive"
                " operation on the data on your disk drive (%s):\n%s\n\n"
                "This is a risky business, so don't proceed if"
                " you have not backed up your important data.\n\n"
                "Continue?") % (dev, text)):
            self.reinit()
            return

        endmark = install.dsize #-1?

        # Tricky logic here! The first partition should be root, then swap then
        # home, but swap and/or home may be absent. The last partition should take
        # its endpoint from 'endmark', root's start from startmark. The actual
        # partitioning should be done, but the formatting can be handled - given
        # the appropriate information - by the installation stage.

        # Remove all existing partitions (except optionally the first)
        install.rmparts(dev, partno)

        if (self.home_mb == 0) and (self.swap_mb == 0):
            em = endmark
        else:
            em = startmark + int(self.rootsize * 1000)
        install.mkpart(dev, startmark, em)
        startmark = em
        install.newPartition("%s%d" % (dev, partno), m='/', f=True)

        install.clearSwaps()
        if (self.swap_mb != 0):
            partno += 1
            if (self.home_mb == 0):
                em = endmark
            else:
                em = startmark + self.swap_mb
            install.mkpart(dev, startmark, em, 'linux-swap')
            startmark = em
            part = "%s%d" % (dev, partno)
            install.addSwap(part, True)

        if self.home_mb:
            partno += 1
            install.mkpart(dev, startmark, endmark)
            install.newPartition("%s%d" % (dev, partno), m='/home', f=True)

        mainWindow.goto('install')


#################################################################

moduleName = 'AutoPart'
moduleDescription = _("Automatic Partitioning")

