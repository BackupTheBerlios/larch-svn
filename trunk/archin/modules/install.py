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
# 2008.01.30

from subprocess import Popen, PIPE
import os
import re

from partition import Partition
from dialogs import PopupInfo

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

            assert (Popen("ssh root@%s /opt/larch/archin/syscalls/test" %
                self.host, shell=True,
                stdout=PIPE).communicate()[0].endswith("^OK^")), (
                    "Couldn't connect to %s" % self.host)

    def xcall_local(self, cmd):
        """Call a function on the same machine.
        """
        return Popen("%s/syscalls/%s" % (basePath, cmd), shell=True,
                stdout=PIPE).communicate()[0]

    def xcall_net(self, cmd, opt=""):
        """Call a function on another machine.
        Public key authentication must be already set up so that no passsword
        is required.
        """
        return Popen("ssh %s root@%s /opt/larch/archin/syscalls/%s" %
                (opt, self.host, cmd), shell=True,
                stdout=PIPE).communicate()[0]   # run the command via ssh

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

            mainWindow.busy()
            os.system(term + cmd)
            mainWindow.busy_off()

    def xcall(self, cmd, opt=""):
        mainWindow.busy()
        if self.host:
            op = self.xcall_net(cmd, opt)
        else:
            op = self.xcall_local(cmd)
        mainWindow.busy_off()
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
                (cluster size (unit for resizing),
                 current volume size,
                 current device size,
                 suggested resize point (minimum))
        All sizes are in bytes.
        When resizing, I suppose it makes sense to select a multiple of
        the cluster size - but this doesn't seem to be necessary.
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
        clus = int(s * 1e6) / self.ntfs_cluster_size
        newsize = clus * self.ntfs_cluster_size

        dev = self.selectedDevice()
        # First a test run
        info = PopupInfo(self.xcall, "ntfs-testrun %s1 %s" % (dev, newsize),
                _("Shrink NTFS partition"), _("Test run ..."))
        if info.result:
            return info.result
        # Now the real thing, resize the file-system
        info = PopupInfo(self.xcall, "ntfs-resize %s1 %s" % (dev, newsize),
                _("Shrink NTFS partition"), _("This is for real ..."))
        if info.result:
            return info.result
        # Now resize the actual partition
        op = self.xcall("getinfo-ntfs1 %s" % dev)
        if not op:
            return _("Couldn't get start of first (NTFS) partition")
        startbyte = int(re.search(r"^1:([0-9]+)B:", op).group(1))
        endbyte = startbyte + newsize - 1
        return self.xcall("part1-resize %s %d %d" % (dev, startbyte, endbyte))

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
        return self.xcall("newpart %s %d %d %s %s" % (dev,
                startMB, endMB, ptype, pl))

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

    def swapFormat(self, p):
        output = self.xcall("swap-format %s" % p)

    def partFormat(self, p, fs):
        output = self.xcall("part-format %s %s" % (p, fs))
