# partauto.py - automatic partitioning stage
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

class AutoPart(Stage, gtk.VBox):
    def stageTitle(self):
        return _("Select installation partitions")

    def getHelp(self):
        return _("The available space will be divided into two or three"
                " partitions. If there is sufficient space a separate home"
                " partition will be created (optionally), to keep user"
                " data separate from system data and programs. This can be"
                " helpful when updating or changing the operating system.\n\n"
                "Also, a 'swap' partition will be created as a"
                " buffer area for situations in which more memory than the"
                " computer actually has is needed - system crashes are thus"
                " avoided, although processing speed will probably be"
                " seriously impaired in such a situation.")

    def __init__(self):
        gtk.VBox.__init__(self)



        self.reinit()




    def reinit(self):
        MINSPLITSIZE = 2e10     # 20 GB
        SWAPSIZE = 1e9          #  1 GB
        HOMESIZE = 50           # % of total

        dev = install.selectedDevice()
        # Info on drive and partitions (dev="/dev/sda", etc.):
        install.getDeviceInfo(dev)
        linuxspace = install.dsize - install.autoPartStart

        self.addLabel(_("Total capacity of drive %s: %6.1f GB") %
                (dev, install.dsize))
        self.addLabel(_("Space available for Arch Linux: %6.1f GB") %
                (float(linuxspace) / 1e9))

        if (linuxspace >= MINSPLITSIZE):
            # Offer option with /home, preactivated.
            # Including slider for adjusting split.

            pass

#?
# Should there be now just 0 or 1 partitions on the device?
        endmark = install.dsize - 1

        if install.autoPartStart:
            # keep 1st partition, allocate from 2nd
            startmark = install.autoPartStart
        else:

            pass
#parted -s /dev/sda unit B  mkpart primary ext2/linux-swap start end

        # Offer manual partitioning
        self.addOption('custom', _("Custom partition selection"))







    def forward(self):
        if (self.part2 and self.part2.get_active()):
            # Keep existing os on 1st partition
            if self.shrink.get_active():
                # Shrink NTFS filesystem
                csize = self.ntfsinfo[0]
                clus = int(self.adj.get_value() * 1e9) / csize
                part2start = clus * csize
                newsize = part2start - install.p1start
                if popupWarning(_("You are about to shrink an NTFS partition.\n"
                        "This is a risky business, so don't proceed if"
                        " you have not backed up your important data.\n\n"
                        "Resize partition?")):
                    message = install.doNTFSshrink(newsize)
                    if message:
                        # resize failed
                        popupMessage(_("Sorry, resizing failed. Here is the"
                                " error report:\n\n") + message)
                        mainWindow.gotoStage('partitions')
                        return

                else:
                    mainWindow.gotoStage('partitions')
                    return

            else:
                part2start = install.p1end + 1

            install.setPart(part2start)
            mainWindow.gotoStage('autoPart')

        elif self.whole.get_active():
            # Use whole drive
            install.setPart(0)
            mainWindow.gotoStage('autoPart')

        else:
            # Manual partitioning
            install.setPart(None)
            mainWindow.gotoStage('manualPart')

    def back(self):
        if (len(install.devices) == 1):
            mainWindow.gotoStage('welcome')
        else:
            mainWindow.gotoStage('devices')

stages['autoPart'] = AutoPart
