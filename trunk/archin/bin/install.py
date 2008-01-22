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
# 2008.01.22

testing=True

import gtk

from subprocess import Popen, PIPE
import os

import re

EXT3DEFAULTS = "NYI"

class installClass:
    def __init__(self, host=None):
        self.host = host
        if self.host:
            if testing:
                op = Popen("ssh root@%s rm -rf /opt/larch/share/syscalls" %
                    self.host, shell=True,
                    stdout=PIPE).communicate()[0]   # delete the (old) commands
                op = Popen("scp -rpq syscalls root@%s:/opt/larch/share/" %
                    self.host, shell=True,
                    stdout=PIPE).communicate()[0]   # copy the commands

            assert (Popen("ssh root@%s /opt/larch/share/syscalls/test" %
                self.host, shell=True,
                stdout=PIPE).communicate()[0].endswith("^OK^")), (
                    "Couldn't connect to %s" % self.host)

    def xcall_local(self, cmd):
        """Call a function on the same machine.
        """
        mainWindow.busy()
        op = Popen("../share/syscalls/" + cmd, shell=True,
                stdout=PIPE).communicate()[0]
        mainWindow.busy_off()
        if op.endswith("^OK^"):
            return ""
        else:
            return op

    def xcall_net(self, cmd, opt=""):
        """Call a function on another machine.
        Public key authentication must be already set up so that no passsword
        is required.
        """
        mainWindow.busy()
        op = Popen("ssh %s root@%s /opt/larch/share/syscalls/%s" %
                (opt, self.host, cmd), shell=True,
                stdout=PIPE).communicate()[0]   # run the command via ssh
        mainWindow.busy_off()
        if op.endswith("^OK^"):
            return ""
        else:
            return op

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
        if self.host:
            return self.xcall_net(cmd, opt)
        else:
            return self.xcall_local(cmd)

    def listDevices(self):
        """Return a list of device descriptions.
        Each device description is a list of strings:
            [device (/dev/sda, etc.),
             size (including unit),
             device type/name]
        """
        devices = []
        op = self.xcall("get-devices")

####### Just for testing!
        if ((not op) and testing):
            op = ("/dev/sda:80.0GB:ATA WDC WD800JB-00JJ;\n"
                    "/dev/sdb:514MB:JetFlash TS512MJF2A/120;\n")

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
        return self.autodevice

    def selectedDeviceSizeString(self):
        return self.devices[self.autodevice][1]

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

####### Just for testing!
        if ((not self.dinfo.startswith("BYT")) and testing):
            self.dinfo = ( "BYT;\n"
                    "/dev/sda:20491MB:scsi:512:512:msdos:ATA Maxtor 2B020H1;\n"
                    "1:0.03MB:15001MB:15001MB:ntfs::;\n"
                    "2:5001MB:7000MB:1999MB:::;\n"
                    "3:7000MB:12001MB:5001MB:::;\n"
                    "1:12001MB:20489MB:8488MB:free;\n")

            self.dinfo2 = ( "BYT;\n"
                    "/dev/sda:80026MB:scsi:512:512:msdos:ATA WDC WD800JB-00JJ;\n"
                    "1:0.03MB:20004MB:20004MB:ntfs::boot;\n"
                    "2:20004MB:40008MB:20004MB:ext3::;\n"
                    "3:40008MB:44005MB:3997MB:linux-swap::;\n"
                    "4:44005MB:80024MB:36019MB:::;\n"
                    "5:44005MB:54007MB:10002MB:ext3::;\n"
                    "6:54007MB:74011MB:20004MB:ext3::;\n"
                    "7:74011MB:80024MB:6013MB:ext3::;\n")

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

####### Just for testing!
            print "get-ntfsinfo failed"
            return (4096, 20003848704, 20003848704, 2310758400)
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
        op = self.xcall("ntfs-testrun %s1 %s" % (dev, newsize))
        if not op:
            return op
        # Now the real thing, resize the file-system
        op = self.xcall("ntfs-resize %s1 %s" % (dev, newsize))
        if not op:
            return op
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
        formatting is done). pl can be 'primary' or 'logical'.
        """
        return self.xcall("newpart %s %d %d %s %s" % (dev,
                startMB, endMB, ptype, pl))

    def clearParts(self):
        """Keep a record of partitions which have been marked for use,
        initially empty.
        """
        self.parts = {}

    def defpart(self, dev, partno, mount, fstype='ext3', format=True,
            flags=EXT3DEFAULTS):
        """Add a partition to the list of those marked for use.
        """
        self.parts["%s%d" % (dev, partno)] = [mount, fstpye, format, flags]
