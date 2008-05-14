# ntfs.py - Resizing of NTS partitions
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
# 2008.05.14


from stage import Stage
from ntfs_gui import NtfsWidget, ShowInfoWidget, PartitionWidget

class Widget(Stage):
    def getHelp(self):
        return _("If a partition is occupied by a Windows operating system"
                " (using the NTFS file-system), you have here the option of"
                " shrinking it to create enough space for Arch Linux.\n"
                "As the automatic partitioning utility only considers space"
                " after the last NTFS partition, it may under certain"
                " circumstances be necessary to delete such a partition,"
                " which can also be done here.\n"
                "If you need more sophisticated partition management you"
                " will have to resort to the manual tools. This automatic"
                " partitioning is only suitable for situations where space"
                " for the new Linux installation is to be allocated at the"
                " end of a disk, after 0 or more NTFS partitions.\n\n"
                "As the operations offered here are potentially quite"
                "destructive please consider carefully before using them.")

    def __init__(self):
        """
        """
        Stage.__init__(self, moduleDescription)

        # Info: NTFS partitions, current partition, total drive size
        self.info = self.addWidget(PartitionWidget())

        # NTFS resizing
        self.ntfs = self.addWidget(NtfsWidget(self.size_changed_cb))

        # Info: space after last NTFS partition
        self.rest = self.addWidget(ShowInfoWidget(
                _("(Potential) free space at end of drive:  ")))

        self.donelist = []
        self.reinit()

    def reinit(self):
        # Detect all NTFS partitions
        self.getNTFSparts()
        # Get simple list of ntfs partitions
        self.partlist = []
        for devs in self.ntfsparts:
            self.partlist += [devs[0] + str(r[0]) for r in devs[3]]
        self.info.set_plist(self.partlist)

        # If no NTFS partition to handle is found, skip this stage
        self.skip = True
        for dev, dsize, csize, parts in self.ntfsparts:
            # Flag last NTFS partition on device
            self.lastpart = True
            for part, t, psize, pstart, pend in parts:
                dpart = dev+str(part)
                if self.lastpart:
                    self.lpsize, self.lpstart, self.lpend = psize, pstart, pend
                if dpart in self.donelist:
                    # Step through partitions
                    self.lastpart = False
                    continue

                self.device = dev
                self.partitionnum = part
                self.dsize = dsize
                self.donelist.append(dpart)
                self.info.set_part(dpart)
                self.info.set_disksize("%8.1f GB" % (float(dsize) / 1000.0))
                self.skip = False

                self.ntfs.set_partsize("%3.1f GB" % (float(psize) / 1000.0))
                self.ntfs.set_delete(False)
                # Set the maximum shrunk size to slightly less than the
                # current partition size
                psize -= 200
                print "reduced psize =", psize
                self.ntfs.set_max(psize)

                # Get occupied space, allow 200MB extra
                ntfsmin = install.getNTFSmin(dpart) + 200
                print "ntfsmin =", ntfsmin
                if (psize < ntfsmin):
                    # Too full to shrink
                    self.ntfs.toofull(True)
                    self.ntfs.set_delete(self.lastpart and
                            ((dsize-pend) < install.LINUXMIN))
                    return

                self.ntfs.toofull(False)
                self.ntfs.set_min(ntfsmin)

                # Whether to shrink by default?
                # Only if it is the last NTFS partition on this disk,
                # and if a fair sharing of free space calls for shrinking,
                # and if it is possible to shrink to the required extent.
                shrinkon = self.lastpart
                # How much to shrink by default?
                # Suggest sharing excess (over the minimum) equally between
                # Linux and Windows
                size = (psize + ntfsmin) / 2
                if self.lastpart:
                    excess = dsize - pstart - ntfsmin
                    if excess < install.LINUXMIN:
                        # The available space is too small, propose
                        # deleting the partition
                        self.ntfs.set_delete(True)
                        size = ntfsmin
                    else:
                        excess -= install.LINUXMIN
                        s = ntfsmin + (excess / 2)
                        if (s < (psize - 500)):
                            # shrink unless change is only minimal
                            size = s
                        else:
                            shrinkon = False

                else:
                    self.set_rest(dsize - self.lpend)

                self.ntfs.set_size(size)
                self.ntfs.set_shrink(shrinkon)
                return

    def set_rest(self, mb):
        self.rest.set("%8.1f GB" % (float(mb) / 1000.0))

    def getNTFSparts(self):
        # Only unmounted partitions will be considered
        mounts = [m.split()[0] for m in install.getmounts().splitlines()
                if m.startswith('/dev/')]
        ld = install.listDevices()
        self.ntfsparts = []
        for d, s, n in ld:
            parts = []
            di = install.getDeviceInfo(d)
            for pi in di[2]:
                # pi: ( partition-number, partition-type,
                #       size in MB, start in MB, end in MB )
                if (pi[1] == 'ntfs'):
                    p = pi[0]
                    if not ((d+str(p)) in mounts):
                        parts.append(pi)
            if parts:
                # Add record for this device:
                #       ( device, disk-size MB, cylinder size MB,
                #         ntfs partition info list )
                parts.reverse()     # So that the last partition comes first
                self.ntfsparts.append((d, di[0], di[1], parts))

    def size_changed_cb(self, size):
        """Called when the requested shrinkage changes, by moving the slider,
        by changing the delete flag, by changing the shrink flag.
        size < 0 => delete
        size = 0 => no shrink
        size > 0 => new shrunk size
        """
        if self.lastpart:
            if (size < 0):
                # This could be wrong, if there is free space before the
                # partition
                rest = self.dsize - self.lpstart
            elif (size == 0):
                rest = self.dsize - self.lpend
            else:
                rest = self.dsize - self.lpstart - size
            self.set_rest(rest)

    def forward(self):
        if self.skip:
            return 0

        # Carry out the requested operation!
        if self.ntfs.deletestate:
            install.rmpart(self.device, self.partitionnum)

        else:
            #????
            pass

        if ((self.device+str(self.partitionnum)) == self.partlist[-1]):
            # Last NTFS partition
            return 0

        self.reinit()
        # Don't go to next stage
        return -1










    def start(self):
        self.ntfs.enable(self.keep1init(self.dev))

        self.swap.enable(True)
        self.setCheck(self.expert, False)
        self.ntfs_changed()
        return self.stop_callback()

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

        # Activate shrinking by default if self.forceshrink is set or
        # less than half the drive is free
        self.ntfs.set_shrink(self.forceshrink or (self.p1end > (self.dsize/2)))

        # Enable retention of the first partition by default
        self.ntfs.set_keep1(True)
        return True

    def keep1_cb(self, on):
        enshrink = (on and not self.noshrink)
        self.ntfs.enable_shrink(enshrink)
        if enshrink and self.ntfs.shrinkstate:
            self.ntfs.enable_shrinkswitch(not self.forceshrink)
        self.ntfs_changed()

    def shrink_cb(self, on):
        self.ntfs_changed()

    def ntfssize_cb(self, size):
        self.ntfs_changed()

    def ntfs_changed(self):
        """Signal a change in ntfssize.
        """
        if not self.ntfsFlag:
            self.ntfsFlag = True
            self.request_update(self.recalculate)

    def swapsize_cb(self):
        self.adjustroot()

    def swap_cb(self, on):
        self.adjustroot()

    def homesize_cb(self):
        self.adjustroot()

    def home_cb(self, on):
        self.adjustroot()

    def adjustroot(self):
        self.rootsize = self.dsize
        if (self.ntfs.is_enabled and self.ntfs.keep1state):
            if self.ntfs.shrinkstate:
                self.rootsize -= self.ntfs.size
            else:
                self.rootsize -= self.p1end

        if (self.swap.is_enabled and self.swap.swapstate):
            self.swap_mb = int(self.swap.size * 1000)
            self.rootsize -= self.swap.size
        else:
            self.swap_mb = 0
        if (self.home.is_enabled and self.home.homestate):
            self.home_mb = int(self.home.size * 1000)
            self.rootsize -= self.home.size
        else:
            self.home_mb = 0
        self.root.set_value(self.rootsize)

    def recalculate(self):
        """Something about the ntfs partition has changed.
        Reevaluate the other partitions. This is an idle callback.
        """
        self.ntfsFlag = False

        MINSPLITSIZE = 20.0    # GB
        SWAPSIZE = 5           # % of total
        SWAPMAX  = 2.0         # GB
        SWAPMAXSIZE = 10       # % of total
        SWAPDEF = 1.0          # GB
        freesize = self.dsize
        if (self.ntfs.is_enabled and self.ntfs.keep1state):
            if self.ntfs.shrinkstate:
                freesize -= self.ntfs.size
            else:
                freesize -= self.p1end

        self.home_on = (freesize >= MINSPLITSIZE)
        home_upper = freesize - SWAPMAX - 5.0
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

        return self.stop_callback()


    def ntfsresize(self):
        """Shrink NTFS filesystem on first partition.
        """
        # convert size to MB
        newsize = int(self.ntfs.size * 1000)
        message = install.doNTFSshrink(newsize)
        if message:
            # resize failed
            popupMessage(_("Sorry, resizing failed. Here is the"
                    " error report:\n\n") + message)
            self.reinit()
            return False
        return True

################################
        if (self.ntfs.is_enabled and self.ntfs.keep1state
                and self.ntfs.shrinkstate):
            if not popupWarning(_("You are about to shrink the"
                    " first partition. Make sure you have backed up"
                    " any important data.\n\nContinue?")):
                return
            if not self.ntfsresize():
                self.reinit()
                return

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

moduleName = 'NtfsShrink'
moduleDescription = _("Shrink or Remove NTFS (Windows) Partition")

