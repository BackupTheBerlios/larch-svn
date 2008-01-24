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
# 2008.01.24

class SelPart(Stage):
    def stageTitle(self):
        return _("Select installation partitions")

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
        Stage.__init__(self)
        from selpart_gui import SelTable, SelDevice

        self.addWidget(SelDevice(self, install.devices))

        mountpoints = ('/', '/home', '/boot', '/var', '/opt', '/usr', '/mnt/%')
        filesystems = ('ext3', 'reiserfs', 'ext2', 'jfs', 'xfs')
        self.table = SelTable(self, mountpoints, filesystems)
        self.addWidget(self.table)
        self.reinit()

    def reinit(self):
        self.mounts = install.getmounts()
        self.setDevice(install.selectedDevice())

    def setDevice(self, dev):
        self.device = dev
        install.getDeviceInfo(self.device)

        self.parts = []
        for p in install.getlinuxparts(self.device):
            if not self.ismounted(p):
                pa = install.getPartition(p)
                if not pa:
                    partno = int(re.sub("/dev/[a-z]+", "", p))
                    size, fstype = install.getPartInfo(partno)
                    pa = install.newPartition(p, size, fstype)
                self.parts.append(pa)

        self.table.renew(self.parts)

    def ismounted(self, part):
        return re.search(r'^%s ' % part, self.mounts, re.M)






# Not so sure any more about 'saving' the settings, as I am now working
# directly on the objects. When it actually comes to the formatting, etc.,
# I would then need to filter the set, though.

    def device_cb(self, dev):
        self.save_settings()
        self.setDevice(dev)

    def save_settings(self):
        # Any partitions with format and/or mount-point need to be entered
        # into the (install) partitions set. All the others should be
        # removed if they are already in that set.
        for p, v in self.parts.items():
            if (v[2] or v[4]):
                install.setPartEntry(p, v[2:])
            elif install.getPartEntry(p):
                install.setPartEntry(p, None)




    def forward(self):
        sel = self.getSelectedOption()
        if (sel == 'done'):
            # prepare and process info
            #...
            # ... install.newPartition("%s%d" % (dev, partno), m='/home')

            mainWindow.goto('install')
            return



stages['partSelect'] = SelPart
