# selpart.py - select partitions manually
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
# 2008.02.27

from stage import Stage
from selpart_gui import SelTable, SelDevice
import partition

class Widget(Stage):
    def getHelp(self):
        return _("The device partitions used for the Arch Linux installation"
                " can be manually selected here.\n"
                "There must be at least an adequately large root ('/')"
                " partition, but the system can be split over a number of"
                " partitions, for example it is often desirable to have a"
                " separate '/home' partition to keep user data separate"
                " from system data and programs. This can be"
                " helpful when updating or changing the operating system.\n\n"
                "Also fairly common are separate partitions for one or more"
                " of '/boot', '/opt', '/usr', '/var', but it is advisable to"
                " inform yourself of the pros and cons before"
                " considering these.")

    def __init__(self):
        Stage.__init__(self, moduleDescription)

        self.device = None
        # List of partitions already configured for use.
        #    Each entry has the form [mount-point, device, format,
        #                         format-flags, mount-flags]
        self.used_partitions = []
        parts = install.get_config("partitions", False)
        if parts:
            for p in parts.splitlines():
                self.used_partitions.append(p.split(':'))

        self.devselect = SelDevice([d[0] for d in install.listDevices()],
                self.setDevice)
        self.addWidget(self.devselect, False)

        filesystems = ['ext3', 'reiserfs', 'ext2', 'jfs', 'xfs']
        # List of mount-point suggestions
        mountpoints = ['/', '/home', '/boot', '/var', '/opt', '/usr']

        self.table = SelTable(filesystems, mountpoints)
        self.addWidget(self.table)
        self.mounts = install.getmounts()

    def setDevice(self, dev):
        if self.device:
            self.tidy()
        self.device = dev
        dinfo = install.getDeviceInfo(self.device)
        pinfo = install.getParts(self.device)
        self.parts = []
        for p in install.getlinuxparts(self.device):
            if not self.ismounted(p):

                partno = int(re.sub("/dev/[a-z]+", "", p))
                for pi in pinfo:
                    size = 0
                    fstype = "?"
                    if (pi[0] == partno):
                        size = pi[2] * dinfo[3] # bytes
                        fstype = pi[1]
                        break

                mountp = ""
                format = ""
                fflags = ""
                mflags = ""
                for pc in self.used_partitions:
                    if (pc[1] == p):
                        mountp = pc[0]
                        format = pc[2]
                        fflags = pc[3]
                        mflags = pc[4]
                        break

                self.parts.append([p, mountp, size, fstype, format,
                        fflags, mflags])

        self.table.renew(self.parts)

    def ismounted(self, part):
        return re.search(r'^%s ' % part, self.mounts, re.M)

    def tidy(self):
        """Save the information on the partitions in use on the current
        device to the config file "partitions".
        """
        # Remove all partitions on the current device from self.used_partitions
        # and add all those with a mount-point (I am assuming I only allow
        # formatting if at the same time a mount-point is specified).
        new = []
        for p in self.used_partitions:
            if not p[1].startswith(self.device):
                new.append(p)
        for p in self.parts:
            if p[1]:
                new.append([p[1], p[0], p[4], p[5], p[6]])
        self.used_partitions = new
        config = ""
        for p in self.used_partitions:
            if config:
                config += "\n"
            config += "%s:%s:%s:%s:%s" % p
        install.set_config("partitions", config)










    def forward(self):
        for p in install.parts.values():
            if (p.mountpoint == '/'):


                # save partition info

                return 0

        popupError(_("You must specify a root ('/') partition"))
        return -1


#################################################################

moduleName = 'MountPoints'
moduleDescription = _("Select Installation Partitions")
