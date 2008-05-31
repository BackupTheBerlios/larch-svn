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
# 2008.05.30

from stage import Stage
from selpart_gui import PartitionGui, SelTable, SelDevice

import re

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
        self.mounts = install.getmounts()
        # List of partitions already configured for use.
        #    Each entry has the form [mount-point, device, format,
        #                         format-flags, mount-flags]
        self.used_partitions = []
        parts = install.get_config("partitions", False)
        if parts:
            for p in parts.splitlines():
                self.used_partitions.append(p.split(':'))

        self.table = SelTable(self)
        self.devselect = SelDevice([d[0] for d in install.listDevices()],
                self.setDevice)
        self.addWidget(self.devselect, False)

        self.addWidget(self.table)

    def setDevice(self, dev):
        if self.device:
            self.tidy()
        self.device = dev
        dinfo = install.getDeviceInfo(self.device)
        pinfo = install.getParts(self.device)
        self.table.clear()
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

                self.table.addrow(Partition(self, p, mountp, size,
                        fstype, format, fflags, mflags))

        self.table.showtable()

    def ismounted(self, part):
        return re.search(r'^%s ' % part, self.mounts, re.M)

    def update_parts(self, partobj):
        """Update the information in the partition list (self.used_partitions)
        for the given partition.
        """
        i = 0
        for p in self.used_partitions:
            if (p[1] == partobj.partition):

                if partobj.mountpoint:
                    # update all info
                    p[0] = partobj.mountpoint
                    p[2] = partobj.newformat
                    p[3] = partobj.format_options
                    p[4] = partobj.mount_options

                else:
                    # remove from list
                    del(self.used_partitions[i])

                return

            i += 1

        # else add this partition
        self.used_partitions.append([partobj.mountpoint,
                partobj.partition, partobj.newformat,
                partobj.format_options, partobj.mount_options])

    def tidy(self):
        """Update the information on the partitions in use as stored in
        the config file "partitions".
        """
        config = ""
        for p in self.used_partitions:
            if config:
                config += "\n"
            config += "%s:%s:%s:%s:%s" % p
        install.set_config("partitions", config)

    def forward(self):
        self.tidy()
        for p in self.used_partitions:
            if (p[0] == '/'):
                return 0

        popupError(_("You must specify a root ('/') partition"))
        return -1


class Partition(PartitionGui):
    """The instances of this class manage the formatting/mount
    information for a single partition.
    """
    def __init__(self, master, p, mountp, size, fstype, format,
            fflags, mflags):
        self.master = master
        self.partition = p
        self.mountpoint = mountp
        self.size = size        # bytes
        self.existing_format = fstype
        self.newformat = format
        self.format_options = fflags
        self.mount_options = mflags

        PartitionGui.__init__(self)

    def get_mount_options(self):
        mopts = []
        if self.mountpoint:
            # Options only available if mount-point is set and partition
            # has (or will have) a file-system
            fl = self.mount_flags()
            if fl:
                lowermo = self.mount_options.lower()
                for name, flag, on, desc in fl:
                    if flag in lowermo:
                        on = flag.upper() in self.mount_options
                    mopts.append((name, flag, on, desc))
        return mopts

    def get_format_options(self):
        fopts = []
        if self.newformat:
            # Options only available if format box is checked, which
            # ensures that self.newformat is set
            fl = self.format_flags(self.newformat)
            if fl:
                lowerfo = self.format_options.lower()
                for name, flag, on, desc in fl:
                    if flag in lowerfo:
                        on = flag.upper() in self.format_options
                    fopts.append((name, flag, on, desc))
        return fopts


    def format_flags(self):
        """Return a list of available format flags for the given
        file-system type.
        """
        # At the moment there is only an entry for 'ext3'
        return { 'ext3' : [
                (_("disable boot-time checks"), 'c', False,
                    _("Normally an ext3 file-system will be checked every"
                      " 30 mounts or so. With a large partition this can"
                      " take quite a while, and some people like to disable"
                      " this and just rely on the journalling.")),

                (_("directory indexing"), 'i', True,
                    _("This is supposed to speed up access.")),

                (_("full journal"), 'f', False,
                    _("This is supposed to increase data safety, at some"
                      " small cost in speed (and disk space?)"))
                ],
            }.get(self.newformat)

    def mount_flags(self):
        """Return a list of available mount (/etc/fstab) flags for the
        given file-system type.
        """
        # At the moment there are just these three flags
        if self.newformat or self.existing_format:
            flg = [ (_("noatime"), 'a', True,
                    _("Disables recording atime (access time) to disk, thus"
                      " speeding up disk access. This is unlikely to cause"
                      " problems (famous last words ...). Important for"
                      " flash devices")),

                    (_("nodiratime"), 'd', True,
                    _("Disables recording directory access time to disk, thus"
                      " speeding up disk access. This is unlikely to cause"
                      " problems (famous last words ...). Important for"
                      " flash devices")),

                    (_("noauto"), 'm', False,
                    _("Don't mount this partition during system"
                      " initialization."))
                ]

            # And nothing file-system specific
            return flg
        else:
            return None

    def set_mount_flags(self, mflags):
        self.mount_options = mflags

    def set_format_flags(self, fflags):
        self.format_options = fflags

    def format_cb(self, fstype):
        """Called from the gui when the formatting option is (de)activated.
        """
        if fstype:
            self.newformat = fstype
            if (fstype != self.existing_format):
                self.format_options = self.default_flags(self.format_flags())
                self.mount_options = self.default_flags(self.mount_flags())
        else:
            if (self.newformat != self.existing_format):
                self.format_options = ""
                self.mount_options = ""
            self.newformat = ""

    def default_flags(self, flist):
        """Return the default set of flags for the given list of flags
        (output of mount_flags or format_flags).
        """
        flags = ''
        if flist:
            for f in flist:
                flags += f[1].upper() if f[2] else f[1]
        return flags

    def mountpoint_cb(self, m):
        if m.startswith('/'):
            # set default mount options
            self.mount_options = self.default_flags(self.mount_flags())
            self.mountpoint = m
        else:
            self.mountpoint = ""
            self.mount_options = ""


#################################################################

moduleName = 'MountPoints'
moduleDescription = _("Select Installation Partitions")
