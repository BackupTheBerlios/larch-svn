# partitions.py - select automatic or manual partitioning stage
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

class Partitions(Stage):
    def stageTitle(self):
        return _("Choose partitioning scheme")

    def getHelp(self):
        return _("Here you can choose which part(s) of the disk(-like)"
                " device to use for the Arch Linux installation.\n\n"
                "WARNING: If you have an operating system already installed"
                " on this drive which you wish to keep, you must choose"
                " 'expert' partitioning, unless the existing operating"
                " system is on the first partition ONLY, and uses the NTFS"
                " file-system (Windows).\n\n"
                "If the first partition (alone) is occupied by a Windows"
                " operating system, you have here the option of shrinking it"
                " to create enough space for Arch Linux.")

    def __init__(self):
        """Things could have changed if we return to this stage, so
        all the setting up of the data is done in 'reinit'.
        """
        Stage.__init__(self)
        from partitions_gui import NtfsWidget, SwapWidget, HomeWidget, RootWidget

        # Info: total drive size
        self.totalsize = self.addLabel("", 'right')

        # NTFS resizing
        self.ntfs = self.addWidget(NtfsWidget(self))

        # swap size
        self.swap = self.addWidget(SwapWidget(self))

        # home size
        self.home = self.addWidget(HomeWidget(self))

        # root size
        self.root = self.addWidget(RootWidget(self))

        # Manual partitioning
        self.expert = self.addCheckButton(_("'Expert' (manual) partitioning"),
            self.expert_cb)

        self.reinit()

    def reinit(self):
        self.ntfsFlag = False   # Used for flagging update requests
        install.clearParts()    # Clear list of assigned partitions

        dev = install.selectedDevice()
        # Info on drive and partitions (dev="/dev/sda", etc.):
        install.getDeviceInfo(dev)
        self.dsize = float(install.dsize) / 1000
        self.setLabel(self.totalsize, _("Total capacity of drive %s:"
                " %6.1f GB  ") % (dev, self.dsize))

        self.ntfs.enable(self.keep1init(dev))

        self.swap.set_on(True)
        self.home.set_on(True)
        self.setCheck(self.expert, False)

    def keep1init(self, dev):
        """Only offer to keep first partition if:
            (a) part1 is NTFS, and (b) potential free space > MINLINUXSIZE
        Return True if the option is to be offered.
        """
        self.noshrink = False
        self.forceshrink = False
        self.p1end = 0.0

        MINLINUXSIZE = 5.0      # GB
        if not install.p1end:
            return False        # part1 not NTFS

        self.p1end = float(install.p1end) / 1000

        # Get lowest possible new end point for partition
        ntfsmin = float(install.getNTFSmin(dev+"1") + install.p1start) / 1000
        valmin = ntfsmin + 0.2
        space = ((self.dsize - valmin) >= MINLINUXSIZE)
                # enough (potential) free space?

        valmax = self.p1end - 0.1
        self.forceshrink = ((self.dsize - self.p1end) < MINLINUXSIZE)
        if self.forceshrink:
            # keeping only possible by shrinking
            valmax = self.dsize - MINLINUXSIZE

        self.noshrink = (valmax < valmin)
                # No shrinking possible, partition too full?
        if self.noshrink or not space:
            popupMessage(_("The option to reduce the size of the existing"
                    " operating system is not available because its"
                    " partition is too full."))
            return space

        # slider values
        val = self.dsize / 2
        if (valmax < val):
            val = valmax
        elif (valmin > val):
            val = valmin
        self.ntfs.set_shrinkadjust(lower=valmin, upper=valmax, value=val)

        # Activate shrinking by default if less than half the drive is free
        self.ntfs.set_shrink(self.p1end > (self.dsize/2))
        return True

    def keep1_cb(self, on):
        enshrink = (on and not self.noshrink)
        self.ntfs.enable_shrinkframe(enshrink)
        if enshrink:
            if self.ntfs.get_shrink_on():
                self.ntfssize = self.ntfs.get_shrinkadjust()
                if self.forceshrink:
                    self.ntfs.enable_shrinkswitch(False)
            else:
                self.ntfssize = self.p1end
                self.ntfs.enable_shrinkadjust(False)
        elif on:
            self.ntfssize = self.p1end
        else:
            self.ntfssize = 0.0
        self.ntfs_changed()

    def shrink_cb(self, on):
        self.ntfs.enable_shrinkadjust(on)
        if on:
            self.ntfssize = self.ntfs.get_shrinkadjust()
        else:
            self.ntfssize = self.p1end
        self.ntfs_changed()

    def ntfssize_cb(self, size):
        self.ntfssize = size
        self.ntfs_changed()

    def ntfs_changed(self):
        """Signal a change in ntfssize.
        """
        if not self.ntfsFlag:
            self.ntfsFlag = True
            self.request_update(self.recalculate)

    def swapsize_cb(self, size):
        self.swapsize = size
        self.adjustroot()

    def swap_cb(self, on):
        self.swapsize = self.swap.get_value()
        self.swap.enable_adjust(on)
        self.adjustroot()

    def homesize_cb(self, size):
        self.homesize = size
        self.adjustroot()

    def home_cb(self, on):
        self.homesize = self.home.get_value()
        self.home.enable_adjust(on)
        self.adjustroot()

    def expert_cb(self, on):
        self.home.enable(not on)
        self.swap.enable(not on)

    def adjustroot(self):
        self.rootsize = self.dsize
        if self.ntfs.isenabled():
            self.rootsize -= self.ntfssize
        if (self.swap.isenabled() and self.swap.get_on()):
            self.rootsize -= self.swapsize
        if (self.home.isenabled() and self.home.get_on()):
            self.rootsize -= self.homesize
        self.root.set_value(self.rootsize)

    def recalculate(self):
        """Something about the ntfs partition has changed.
        Reevaluate the other partitions. This is an idle callback.
        """
        self.ntfsFlag = False

        MINSPLITSIZE = 20.0    # GB
        HOMESIZE = 50          # % of total
        SWAPSIZE = 5           # % of total
        SWAPMAX  = 4.0         # GB
        SWAPMAXSIZE = 10       # % of total
        SWAPDEF = 1.0          # GB
        freesize = self.dsize - self.ntfssize

        home_on = (freesize >= MINSPLITSIZE)
        home_upper = freesize - SWAPMAX - 5.0
        home_value = freesize * HOMESIZE / 100
        self.home.set_adjust(upper=home_upper, value=home_value)
        if not self.getCheck(self.expert):
            self.home.enable(home_on)

        swap_upper = freesize * SWAPMAXSIZE / 100
        if (swap_upper > SWAPMAX):
            swap_upper = SWAPMAX
        swap_value = freesize * SWAPSIZE / 100
        if (swap_value > SWAPDEF):
            swap_value = SWAPDEF
        self.swap.set_adjust(upper=swap_upper, value=swap_value)

        return self.stop_callback()

    def forward(self):
        if self.expert.get_active():
            mainWindow.goto('manualPart')
            return

        # Set up the installation partitions automatically.
        # If NTFS resizing is to be done, do it now.
        if self.ntfs.get_keep1_on():
            # Keep existing os on 1st partition

            if self.ntfs.get_shrink_on():
            # Shrink NTFS filesystem, convert size to MB
                newsize = int(self.ntfssize * 1000)
                if popupWarning(_("You are about to shrink an NTFS partition.\n"
                        "This is a risky business, so don't proceed if"
                        " you have not backed up your important data.\n\n"
                        "Resize partition?")):
                    message = install.doNTFSshrink(newsize)
                    if message:
                        # resize failed
                        popupMessage(_("Sorry, resizing failed. Here is the"
                                " error report:\n\n") + message)
                        self.reinit()
                        return

                else:
                    self.reinit()
                    return

            # keep 1st partition, allocate from 2nd
            startmark = install.p1end # valid?
            partno = 2

        else:
            startmark = 0
            partno = 1

        endmark = install.dsize #-1?

        # Tricky logic here! The first partition should be root, then swap then
        # home, but swap and/or home may be absent. The last partition should take
        # its endpoint from 'endmark', root's start from startmark. The actual
        # partitioning should be done, but the formatting can be handled - given
        # the appropriate information - by the installation stage.

        # Remove all existing partitions (except optionally the first)
        dev = install.selectedDevice()
        install.rmparts(dev, partno)

        if (self.homesize == 0) and (self.swapsize == 0):
            em = endmark
        else:
            em = startmark + int(self.rootsize * 1000)
        install.mkpart(dev, startmark, em)
        startmark = em
        install.newPartition("%s%d" % (dev, partno), m='/', f=True)

        if (self.swapsize != 0):
            partno += 1
            if (self.homesize == 0):
                em = endmark
            else:
                em = startmark + int(self.swapsize * 1000)
            install.mkpart(dev, startmark, em, 'linux-swap')
            startmark = em

        if self.homesize:
            partno += 1
            install.mkpart(dev, startmark, endmark)
            install.newPartition("%s%d" % (dev, partno), m='/home', f=True)

        mainWindow.goto('install')


#################################################################

stages['partitions'] = Partitions

