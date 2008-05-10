# finddevices.py - discover possible (disk-like) installation devices
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
# 2008.05.10

from stage import Stage
from dialogs import popupError, popupMessage

class Widget(Stage):
    def __init__(self):
        Stage.__init__(self, moduleDescription)
        self.message = self.addReportWidget()
        self.message.report(_('Searching for disk(-like) devices'
                ' and currently mounted partitions.\n'
                'If a device line starts with "*", one or more of its'
                ' partitions are currently\nmounted and this device'
                ' will not be offered for automatic partitioning.\n\n'))
        mainWindow.busy_on()
        self.getDevices()
        mainWindow.busy_off()

    def getHelp(self):
        return _('An automatically calculated default partitioning scheme'
                ' will be offered on the basis of the discovered drives and'
                ' partitions. A very limited amount of tweaking to this'
                ' scheme is possible.\n'
                ' Only devices with no mounted partitions will be offered'
                ' for automatic partitioning.\n'
                ' If you want more control over the partitioning of your disk'
                ' drives and the location of the installation, you will'
                ' need to use an external tool. cfdisk and gparted'
                ' should normally be available for partitioning. The'
                ' selection of the mount points can then be done in the'
                ' "Set Mount Points" stage, which will be skipped if the'
                ' default partitioning scheme is accepted.')

    def forward(self):
        if (self.devcount == 1):
            mainWindow.setStage('Partitions')
        elif (self.devcount == 0):
            mainWindow.setStage('ManualPart')
        else:
            mainWindow.setStage('Devices')

    def getDevices(self):
        larchdev = install.larchdev().rstrip('0123456789')
        larchcount = 0
        devs = []
        ld = install.listDevices()
        # Note that if one of these has mounted partitions it will not be
        # available for automatic partitioning, and should thus not be
        # included in the list used for automatic installation
        mounts = install.getmounts().splitlines()
        self.devcount = 0
        if ld:
            for d, s, n in ld:
                self.devcount += 1
                # Mark devices which have mounted partitions
                dstring = "%16s  (%10s : %s)" % (d, s, n)
                dm = " "
                for m in mounts:
                    if m.startswith(d):
                        if (d == larchdev):
                            larchcount = 1
                        d += "-"
                        dm = "*"
                        self.devcount -= 1
                        break
                devs.append([d, s, n])
                self.message.report(dm + dstring)
            install.setDevices(devs)

        if not devs:
            popupError(_("No disk(-like) devices were found,"
                    " so Arch Linux can not be installed on this machine"))
            install.tidyup()
        nds = len(devs)         # Total number of devices
        mds = nds - self.devcount   # Number of devices with mounted partitions
        mds2 = mds - larchcount # Number excluding the larch boot device

        if mds2:
            self.message.report(_("\n\n%d devices were found with mounted"
                    " partitions.\n"
                    "These devices are not available for automatic"
                    " partitioning,\nyou must partition them manually.")
                    % mds)

        install.setDevice(None)
        if (self.devcount == 1):
            for d, s, n in devs:
                if not d.endswith('-'):
                    install.setDevice(d)
                    break


#################################################################

moduleName = 'FindDevices'
listed = True
moduleDescription = _("Disk Discovery")
