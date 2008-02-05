# install.py
#
# This module handles communication with the system on which Arch is to
# be installed, which can be different to the one on which archin is
# running.
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
# 2008.02.05

from subprocess import Popen, PIPE, STDOUT
import os
import re

from partition import Partition
from dialogs import PopupInfo, popupWarning

class installClass:
    def __init__(self, host=None, transfer=False):
        self.host = host
        if self.host:
            if transfer:
                op = Popen("ssh root@%s rm -rf /opt/larch/archin" %
                    self.host, shell=True,
                    stdout=PIPE).communicate()[0]   # delete (old) archin
                op = Popen("scp -rpq %s root@%s:/opt/larch/" %
                    (basePath, self.host), shell=True,
                    stdout=PIPE).communicate()[0]   # copy archin over

        assert (self.xcall("init") == ""), (
                "Couldn't initialize installation system")

        # Allow possibility of offering 'frugal' installation.
        self.frugal = False

    def xcall_local(self, cmd):
        """Call a function on the same machine.
        """
        xcmd = ("%s/syscalls/%s" % (basePath, cmd))
        return Popen(xcmd, shell=True, stdout=PIPE, stderr=STDOUT)

    def xcall_net(self, cmd, opt=""):
        """Call a function on another machine.
        Public key authentication must be already set up so that no passsword
        is required.
        """
        xcmd = ("ssh %s root@%s /opt/larch/archin/syscalls/%s" %
                (opt, self.host, cmd))
        return Popen(xcmd, shell=True, stdout=PIPE, stderr=STDOUT)

    def terminal(self, cmd):
        """Run a command in a terminal. The environment variable 'XTERM' is
        recognized, otherwise one will be chosen from a list.
        """
        term = os.environ.get("XTERM", "")
        if (os.system("which %s &>/dev/null" % term) != 0):
            for term in ("terminal", "konsole", "xterm", "rxvt", "urxvt"):
                if (os.system("which %s &>/dev/null" % term) != 0):
                    term = None
                else:
                    break

            assert term, "No terminal emulator found"
            if (term == "terminal"):
                term += " -x "
            else:
                term += " -e "

            process = Popen(term + cmd, shell=True)
            while (process.poll() == None):
                mainWindow.eventloop(0.5)


    def xcall(self, cmd, opt="", callback=None):
        if self.host:
            process = self.xcall_net(cmd, opt)
        else:
            process = self.xcall_local(cmd)

        while (process.poll() == None):
            if callback:
                callback()
            mainWindow.eventloop(0.5)

        op = process.stdout.read()
        if op.endswith("^OK^"):
            self.okop = op
            return ""
        else:
            return op

    def listDevices(self):
        """Return a list of device descriptions.
        Each device description is a list of strings:
            [device (/dev/sda, etc.),
             size (including unit),
             device type/name]
        """
        devices = []
        op = self.xcall("get-devices")
        for line in op.splitlines():
            devices.append(line.rstrip(';').split(':'))
        return devices

    def getmounts(self):
        return self.xcall("get-mounts")

    def setDevices(self, devs):
        """Set the self.devices list.
        """
        self.devices = devs

    def larchdev(self):
        """If the running system is larch, return the device from which
        it booted. Otherwise ''.
        """
        return self.xcall("larchbootdev").strip()

    def setDevice(self, device):
        """Set device selection for automatic partitioning.
        The value is the name of the drive ('/dev/sda', etc.).
        None is also a possibility ...
        """
        self.autodevice = device

    def selectedDevice(self):
        return self.autodevice or self.devices[0][0]

    def setPart(self, start):
        """Used by the autopartitioner to determine where the free space
        begins. The value can be:
                None       - manual partitioning
                0          - use whole drive
                1          - start after first partition
        """
        self.autoPartStart = start

    def getDeviceInfo(self, dev):
        # Info on drive and partitions (dev="/dev/sda", etc.):
        self.dinfo = self.xcall("get-partitions %s" % dev)
        # get the drive size in MB
        dsm = re.search(r"^/dev.*:([0-9\.]+)MB:.*;$", self.dinfo, re.M)
        self.dsize = int(dsm.group(1).split('.')[0])
        # get the info for the first partition, but only if it is NTFS
        p1m = re.search(r"^1:([0-9\.]+)MB:([0-9\.]+)MB:"
                "([0-9\.]+)MB:ntfs:.*;$", self.dinfo, re.M)
        if p1m:
            self.p1size = int(p1m.group(3).split('.')[0])
            self.p1start = int(p1m.group(1).split('.')[0])
            self.p1end = int(p1m.group(2).split('.')[0])
        else:
            self.p1size = 0
            self.p1start = 0
            self.p1end = 0
        # Also get the size of a cylinder, convert to MB
        c, m = self.xcall("get-cylsize %s" % dev).split()
        self.cylinders = int(c)
        self.cylinderMB = float(m) / 1000

    def getPartInfo(self, partno):
        """Get size and fstype for the given partition number using the
        data from the last call of getDeviceInfo.
        """
        rc = re.compile(r"^%d:([0-9\.]+)MB:([0-9\.]+)MB:"
                "([0-9\.]+)MB:([^:]*):.*;$" % partno)
        for l in self.dinfo.splitlines():
            rm = rc.search(l)
            if (rm and (rm.group(4) != 'free')):
                size = int(rm.group(3))
                fstype = rm.group(4)
                return (size, fstype)
        # This shouldn't happen
        assert False, "I wasn't expecting the Spanish Inquisition"

    def getNTFSinfo(self, part):
        """Return information about the given partition as a tuple:
                (cluster size (unit for resizing?),
                 current volume size,
                 current device size,
                 suggested resize point (minimum))
        All sizes are in bytes.
        When resizing, I suppose it makes sense to select a multiple of
        the cluster size - but this doesn't seem to be necessary. For
        other reasons - it seems to be standard - I have decided to make
        partitions start on (even?) cylinder boundaries.

        If the call fails for some reason, None is returned.
        """
        op = self.xcall("get-ntfsinfo %s" % part)
        rx = re.compile(r"^[^0-9]* ([0-9]+) ")
        lines = op.splitlines()
        try:
            self.ntfs_cluster_size = int(rx.search(lines[0]).group(1))
            cvs = int(rx.search(lines[0]).group(1))
            cds = int(rx.search(lines[0]).group(1))
            srp = int(rx.search(lines[0]).group(1))
        except:
            print "get-ntfsinfo failed"
            return None
        return (self.ntfs_cluster_size, cvs, cds, srp)

    def getNTFSmin(self, part):
        """Get the minimum size in MB for shrinking the given NTFS partition.
        """
        cs, cvs, cds, srp = self.getNTFSinfo(part)
        return srp / 1000000

    def doNTFSshrink(self, s):
        """Shrink selected NTFS partition. First the file-system is shrunk,
        then the partition containing it. The given size is in MB.
        """
        # This rounding to whole clusters may well not be necessary
        clus = int(s * 1e6) / self.ntfs_cluster_size
        newsize = clus * self.ntfs_cluster_size

        dev = self.selectedDevice()

        # First a test run
        info = PopupInfo(_("Test run ..."), _("Shrink NTFS partition"))
        res = self.xcall("ntfs-testrun %s1 %s" % (dev, newsize))
        info.drop()
        if res:
            return res

        # Now the real thing, resize the file-system
        info = PopupInfo(_("This is for real, shrinking file-system ..."),
                _("Shrink NTFS partition"))
        res = self.xcall("ntfs-resize %s1 %s" % (dev, newsize))
        info.drop()
        if res:
            return res

        # Now resize the actual partition

        # Get new start of following partition - even cylinder boundary,
        # doing quite a safe rounding up.
        newcyl = (int((newsize / 1e6) / self.cylinderMB + 2) / 2) * 2

        info = PopupInfo(_("Resizing partition ..."),
                _("Shrink NTFS partition"))
        res = self.xcall("part1-resize %s %d" % (dev, newcyl))
        info.drop()
        if res:
            return res

        # And finally expand the ntfs file-system into the new partition
        info = PopupInfo(_("Fitting file-system to new partition ..."),
                _("Shrink NTFS partition"))
        res = self.xcall("ntfs-growfit %s1" % dev)
        info.drop()
        self.getDeviceInfo(dev)
        return res

    def gparted_available(self):
        """Return '' if gparted is available.
        """
        return self.xcall("gparted-available", "-Y")

    def gparted(self):
        return self.xcall("gparted-run", "-Y")

    def cfdisk(self, dev):
        if self.host:
            cmd = "ssh -t root@%s cfdisk %s" % (self.host, dev)
        else:
            cmd = "cfdisk %s" % dev
        self.terminal(cmd)


    def rmparts(self, dev, partno):
        """Remove all partitions on the given device starting from the
        given partition number.
        """
        parts = self.xcall("listparts %s" % dev).splitlines()
        i = len(parts)
        while (i > 0):
            i -= 1
            p = int(parts[i])
            if (p >= partno):
                op = self.xcall("rmpart %s %d" % (dev, p))
                if op: return op
        return ""

    def mkpart(self, dev, startMB, endMB, ptype='ext2', pl='primary'):
        """Make a partition on the given device with the given start and
        end points. The default type is linux (called 'ext2' but no
        formatting is done). pl can be 'primary', 'extended' or 'logical'.
        """
        # Partitions are aligned to even cylinder boundaries
        startcyl = (int(startMB / self.cylinderMB + 1) / 2) * 2
        endcyl = (int(endMB / self.cylinderMB + 1) / 2) * 2
        if (endcyl > self.cylinders):
            endcyl = self.cylinders

        return self.xcall("newpart %s %d %d %s %s" % (dev,
                startcyl, endcyl, ptype, pl))

    def getlinuxparts(self, dev):
        """Return a list of partitions on the given device with linux
        partition code (83).
        """
        return self.xcall("linuxparts %s" % dev).split()

    def clearParts(self):
        """Keep a record of partitions which have been marked for use,
        initially empty.
        """
        self.parts = {}

    def newPartition(self, p, s="?", fpre=None, m=None, f=False, fnew=None,
            mo=None, fo=None):
        """Add a partition to the list of those marked for use.
        """
        pa = Partition(p, s, fpre, m, f, fnew, mo, fo)
        self.parts[p] = pa
        return pa

    def getPartition(self, part):
        return self.parts.get(part)

    def getActiveSwaps(self):
        """Discover active swap partitions. Return list
        of pairs: (device, size(GB)).
        """
        output = self.xcall("get-active-swaps")
        swaps = []
        for l in output.splitlines():
            ls = l.split()
            swaps.append((ls[0], float(ls[1]) * 1024 / 1e9))
        return swaps

    def getAllSwaps(self):
        """Discover swap partitions, whether active or not. Return list
        of pairs: (device, size(GB)).
        """
        # I might want to add support for LVM/RAID?
        output = self.xcall("get-all-swaps")
        swaps = []
        for l in output.splitlines():
            ls = l.split()
            swaps.append((ls[0], float(ls[1]) * 1024 / 1e9))
        return swaps

    def clearSwaps(self):
        self.swaps = []
        self.format_swaps = []

    def addSwap(self, p, format):
        # include in /etc/fstab
        self.swaps.append(p)
        if format:
            self.format_swaps.append(p)

    def swapFormat(self, p):
        return self.xcall("swap-format %s" % p)

    def partFormat(self, p):
        fo = p.format_options
        if (fo == None):
            fo = ""
        return self.xcall("part-format %s %s %s" % (p.partition,
                p.newformat, fo))

    def mount(self, part, mp):
        return self.xcall("do-mount %s %s" % (part, mp))

    def checkEmpty(self, mp):
        if self.xcall("check-mount %s" % mp):
            return popupWarning(_("The partition mounted at %s is not"
                    " empty. This could have bad consequences if you"
                    " attempt to install to it. Please reconsider.\n\n"
                    " Do you still want to install to it?") % mp)
        return True

    def unmount(self, mp):
        return self.xcall("do-unmount %s" % mp)

    def guess_size(self, d='/'):
        """Get some estimate of the size of the given directory d, in MiB.
        """
        return int(self.xcall("guess-size %s" % d))

    def lsdir(self, d):
        """Get a list of items in the given directory ('ls').
        """
        return self.xcall("lsdir %s" % d).split()

    def copyover(self, dir, cb):
        self.xcall("copydir %s" % dir, callback=cb)

    def install_tidy(self):
        self.xcall("larch-tidy")

    def get_size(self):
        """Get some estimate of the current size of the system being
        installed.
        Returns a value in MiB.
        """
        return int(self.xcall("installed-size"))

    def mkinitcpio(self):
        self.xcall("do-mkinitcpio")
