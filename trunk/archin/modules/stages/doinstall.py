# doinstall.py - formatting and installation stage
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
# 2008.01.29

class DoInstall(Stage):
    def stageTitle(self):
        return _("Perform Installation")

    def getHelp(self):
        return _("Here the chosen partitions will be formatted and mounted."
                " Then the running system will be copied onto them.")

    def __init__(self):
        """
        """
        Stage.__init__(self)
        from doinstall_gui import Report
        self.output = Report()

        self.format()

        self.mount()

        assert False, "NYI"

# reinit? Some message saying that the system has already been installed,
# so no possible action?



    def format(self):
        # Swaps
        for p in install.format_swaps:
            self.output.report(_("Formatting partition %s as swap ...") % p)
            self.output.report(install.swapFormat(p))

        # Installation partitions
        for p in install.parts:
            if p.format:
                self.output.report(_("Formatting partition %s as %s ...")
                        % (p, p.newformat))
                self.output.report(install.partFormat(p, p.newformat))

    def mount(self):



    def forward(self):
        assert False, "NYI"
        if self.expert.get_active():
            mainWindow.goto('manualPart')
            return

        # Set up the installation partitions automatically.
        # If NTFS resizing is to be done, do it now.
        if self.ntfs.get_keep1_on():
            # Keep existing os on 1st partition

            if self.ntfs.get_shrink_on():
            # Shrink NTFS filesystem, convert size to MB
                newsize = int(self.ntfssize * 1000)
                if popupWarning(_("You are about to shrink an NTFS partition.\n"
                        "This is a risky business, so don't proceed if"
                        " you have not backed up your important data.\n\n"
                        "Resize partition?")):
                    message = install.doNTFSshrink(newsize)
                    if message:
                        # resize failed
                        popupMessage(_("Sorry, resizing failed. Here is the"
                                " error report:\n\n") + message)
                        self.reinit()
                        return

                else:
                    self.reinit()
                    return

            # keep 1st partition, allocate from 2nd
            startmark = install.p1end # valid?
            partno = 2

        else:
            startmark = 0
            partno = 1

        endmark = install.dsize #-1?

        # Tricky logic here! The first partition should be root, then swap then
        # home, but swap and/or home may be absent. The last partition should take
        # its endpoint from 'endmark', root's start from startmark. The actual
        # partitioning should be done, but the formatting can be handled - given
        # the appropriate information - by the installation stage.

        # Remove all existing partitions (except optionally the first)
        dev = install.selectedDevice()
        install.rmparts(dev, partno)

        if (self.home_mb == 0) and (self.swap_mb == 0):
            em = endmark
        else:
            em = startmark + int(self.rootsize * 1000)
        install.mkpart(dev, startmark, em)
        startmark = em
        install.newPartition("%s%d" % (dev, partno), m='/', f=True)

        if (self.swap_mb != 0):
            partno += 1
            if (self.home_mb == 0):
                em = endmark
            else:
                em = startmark + self.swap_mb
            install.mkpart(dev, startmark, em, 'linux-swap')
            startmark = em

        if self.home_mb:
            partno += 1
            install.mkpart(dev, startmark, endmark)
            install.newPartition("%s%d" % (dev, partno), m='/home', f=True)

        mainWindow.goto('install')


#################################################################

stages['install'] = DoInstall

