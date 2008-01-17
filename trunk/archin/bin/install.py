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
# 2008.01.17

testing=True

import gtk

from subprocess import Popen, PIPE
import os

import re

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

    def getDevices(self):
        """self.devices is set to a list of device descriptions.
        Each device description is a list of strings:
            [device (/dev/sda, etc.),
             size (including unit),
             device type/name]
        """
        self.devices = []
        op = self.xcall("get-devices")

####### Just for testing!
        if ((not op) and testing):
            op = ("/dev/sda:80.0GB:ATA WDC WD800JB-00JJ;\n"
                    "/dev/sdb:514MB:JetFlash TS512MJF2A/120;\n")

        for line in op.splitlines():
            self.devices.append(line.rstrip(';').split(':'))

    def setDevice(self, index):
        """Set device selection for automatic partitioning.
        The value is the index of the device in the 'devices' list.
        """
        self.autodevice = index

    def selectedDevice(self):
        if (self.autodevice < 0):
            return None
        return self.devices[self.autodevice][0]

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
                    "1:0.03MB:5001MB:5001MB:ext2::;\n"
                    "2:5001MB:7000MB:1999MB:::;\n"
                    "3:7000MB:12001MB:5001MB:::;\n"
                    "1:12001MB:20489MB:8488MB:free;\n")

            self.dinfo = ( "BYT;\n"
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
        When resizing, a new partition should start on a cluster boundary?
        (i.e. its 'start' address should be a multiple of the cluster size).
        The first partition is an exception, it seems to start at 32256.
        gparted doesn't do this. It calculates in sectors(?), 512 byte units,
        and it is not clear whether the size should be in full clusters.
        If the call fails for some reason, None is returned.
        """
        op = self.xcall("get-ntfsinfo %s" % part)
        rx = re.compile(r"^[^0-9]* ([0-9]+) ")
        lines = op.splitlines()
        try:
            cs = int(rx.search(lines[0]).group(1))
            cvs = int(rx.search(lines[0]).group(1))
            cds = int(rx.search(lines[0]).group(1))
            srp = int(rx.search(lines[0]).group(1))
        except:

####### Just for testing!
            print "get-ntfsinfo failed"
            return (4096, 20003848704, 20003848704, 2310758400)
            return None
        return (cs, cvs, cds, srp)

    def doNTFSshrink(self, newsize):
        """Shrink selected NTFS partition. First the file-system is shrunk,
        then the partition containing it.
        """
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
        op = self.xcall("part-remove %s" % dev)
        if not op:
            return op
        return self.xcall("part-replace %s" % dev)

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
