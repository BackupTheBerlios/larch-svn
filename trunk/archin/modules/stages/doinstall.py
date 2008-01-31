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
# 2008.01.31

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

        self.ok = (self.format() and self.mount() and self.install() and
                self.unmount())
        if self.ok:
            self.output.report(_("Installation completed successfully."))

    def reinit(self):
        self.output.report(_("The installation has already been completed."
                " No further action is possible."))

    def format(self):
        # Swaps
        for p in install.format_swaps:
            self.output.report(_("Formatting partition %s as swap ...") % p)
            result = install.swapFormat(p)
            if result:
                self.output.report(result)
                return False

        # Installation partitions
        for p in install.parts:
            if p.format:
                self.output.report(_("Formatting partition %s as %s ...")
                        % (p.partition, p.newformat))
                result = install.partFormat(p)
                if result:
                    self.output.report(result)
                    return False

        return True

    def mount(self):
        """The order is important in some cases, so when building the list
        care must be taken that inner mounts (e.g. '/home') are placed
        after their containing mounts (e.g. '/') in the list.
        """
        self.mplist = []
        for p in install.parts:
            if p.mountpoint:
                i = 0
                for p0 in self.mplist:
                    if (p.mountpoint < p0):
                        break
                    i += 1
                self.mplist[i:i] = (p.mountpoint, p.partition)
        for m, d in self.mplist:
            self.output.report(_("Mounting partition %s at %s") % (d, m))
            result = install.mount(d, m)
            if result:
                self.output.report(result)
                return False
        return True

    def unmount(self):
        """To unmount the partitions mounted by the installer.
        """
        mlist = list(self.mplist)
        mlist.reverse()
        for m in mlist:
            # the 'list()' is needed because of the 'remove' below
            self.output.report(_("Unmounting partition %s from %s") % (d, m))
            result = install.unmount(m)
            if result:
                self.output.report(result)
                return False
        return True

    def install(self):
        self.output.report("Actual installation NYI")
        return True



    def forward(self):
        if self.ok:
            mainWindow.goto('grub')
        else:
            mainWindow.goto('error')


#################################################################

stages['install'] = DoInstall

