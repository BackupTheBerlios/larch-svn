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
# 2008.01.23

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
        from selpart_gui import SelTable
        self.table_widget = SelTable
        self.table = None
        self.reinit()

    def reinit(self):
        self.mounts = install.getmounts()
        self.setDevice(install.selectedDevice())

    def setDevice(self, dev):
        self.device = dev
        install.getDeviceInfo(self.device)

        # Create a new partition list/table
        if self.table:
            self.remove(self.table)
        self.table = self.table_widget(self)
        self.addWidget(self.table)

        self.parts = {}
        for p in install.getlinuxparts(self.device):
            if not self.ismounted(p):
                partno = int(re.sub("/dev/[a-z]+", "", p))
                size, fstype = install.getPartInfo(partno)
                pinfo = install.getPart(p)
                # pinfo has the form: [mount, newfstype, format, flags]
                if not pinfo:
                    pinfo = [None, None, False, None]
                # pxinfo has the form: [size (MB), existing fstype,
                #       mount-point, new fstype, format, flags]
                pxinfo = [size, fstype] + pinfo
                self.parts[p] = pxinfo
                self.table.addPart(p, pxinfo)

    def ismounted(self, part):
        return re.search(r'^%s ' % part, self.mounts, re.M)


    def format_cb(self, p, on):
        self.parts[p][4]= on
        if on:
            newfs = self.parts[p][3]
            if not newfs:
                newfs = 'ext3'
                # set flags???


            self.table.set_fstype(p, newfs)

        else:
            self.table.set_fstype(p, self.parts[p][1])
            self.table.enable_fstype(p, False)

    def fstype_cb(self, p, fstype):
        if self.parts[p][4]:
            self.parts[p][3] = fstype
        else:
            self.parts[p][3] = None

    def device_cb(self, dev):
        self.save_settings()
        self.setDevice(dev)

    def save_settings(self):
        # Any partitions with format and/or mount-point need to be entered
        # into the (install) partitions set. All the others should be
        # removed if they are already in that set.
        assert False, "NYI"




    def forward(self):
        sel = self.getSelectedOption()
        if (sel == 'done'):
            # prepare and process info
            #...
            # ... install.defPart("%s%d" % (dev, partno), '/home')

            mainWindow.goto('install')
            return



stages['partSelect'] = SelPart
