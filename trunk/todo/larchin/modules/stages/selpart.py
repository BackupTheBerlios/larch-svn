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
# 2008.02.29

from stage import Stage
from selpart_gui import SelTable, SelDevice

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

                self.parts.append(Partition(p, mountp, size,
                        fstype, format, fflags, mflags)

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
            if p.mountpoint:
                new.append([p.mountpoint, p.partition, p.newformat,
                        p.format_options, p.mount_options])
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


class Partition:
    """The instances of this class manage the formatting/mount
    information for a single partition.
    """
    def __init__(self, p, mountp, size, fstype, format, fflags, mflags)
        self.partition = p
        self.mountpoint = mountp
        self.size = size        # bytes
        self.existing_format = fstype
        self.newformat = format
        self.format_options = fflags
        self.mount_options = mflags

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


#################################################################

moduleName = 'MountPoints'
moduleDescription = _("Select Installation Partitions")
