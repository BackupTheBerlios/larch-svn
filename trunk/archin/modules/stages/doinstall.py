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
# 2008.02.02

class DoInstall(Stage):
    def stageTitle(self):
        return _("Perform Installation")

    def getHelp(self):
        return _("Here the chosen partitions will be formatted and mounted."
                " Then the running system will be copied onto them.")

    def labelL(self):
        return ""

    def __init__(self):
        """
        """
        Stage.__init__(self)
        from doinstall_gui import Report, Progress
        self.output = Report()
        self.addWidget(self.output)

        self.progress = Progress()
        self.addWidget(self.progress, False)
        self.request_soon(self.run)

    def run(self):
        # need to disable forward button
        mainWindow.enable_forward(False)
        self.ok = (self.format() and self.mount() and self.install() and
                self.unmount())
        if self.ok:
            self.output.report(_("Installation completed successfully."))
        self.output.report(_("Press 'Forward' to continue"))
        # need to reenable forward button
        mainWindow.enable_forward(True)
        return self.stop_callback()

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
        for p in install.parts.values():
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
        for p in install.parts.values():
            if p.mountpoint:
                i = 0
                for p0 in self.mplist:
                    if (p.mountpoint < p0):
                        break
                    i += 1
                self.mplist.insert(i, (p.mountpoint, p.partition))
        for m, d in self.mplist:
            self.output.report(_("Mounting partition %s at %s") % (d, m))
            result = install.mount(d, m)
            if result:
                self.output.report(result)
                return False
            # Check that there are no files on this partition. The warning
            # can be ignored however.
            if not install.checkEmpty(m):
                return False
        return True

    def unmount(self):
        """To unmount the partitions mounted by the installer.
        """
        mlist = list(self.mplist)
        mlist.reverse()
        for m, d in mlist:
            # the 'list()' is needed because of the 'remove' below
            self.output.report(_("Unmounting partition %s from %s") % (d, m))
            result = install.unmount(m)
            if result:
                self.output.report(result)
                return False
        return True

    def install(self):
        from time import sleep
        self.system_size = install.guess_size()
        self.output.report("%s: %d MiB" % (_("Estimated install size"),
                self.system_size))
        self.output.report(_("Starting actual installation ..."))
        self.progress.start()
        self.progress_count = 0
        install.start_install(self.progress_cb)
        self.output.report(_("Copying of system completed."))
        self.output.report(_("Generating initramfs"))
        install.mkinitcpio()
        return True

    def progress_cb(self):
        self.progress_count += 1
        if self.progress_count < 10:
            return
        self.progress_count = 0

        installed_size = install.get_size()
        frac = float(installed_size) / self.system_size
        if (frac > 1.0):
            frac = 1.0
        self.progress.set(frac)

    def forward(self):
        if self.ok:
            mainWindow.goto('grub')
        else:
            mainWindow.goto('error')


#################################################################

stages['install'] = DoInstall

