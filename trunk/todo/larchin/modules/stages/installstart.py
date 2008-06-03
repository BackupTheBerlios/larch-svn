# installstart.py - summarize formatting and installation partitions
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
# 2008.06.03

from stage import Stage

class Widget(Stage):
    def getHelp(self):
        return _("If you press OK now the chosen partitions will be"
                " formatted and mounted and then the running system will"
                " be copied onto them.")

    def __init__(self):
        Stage.__init__(self, moduleDescription)

        self.addLabel(_("Please check that the formatting of the"
                " following partitions and their use within the new"
                " installation (mount-points) corresponds with what you"
                " had in mind. Accidents could well result in serious"
                " data loss."))

class PartTable(gtk.TreeView):
    """This widget presents a list of partitions to be formatted and/or
    mounted for the installation.
    """
    def __init__(self):
        gtk.TreeView.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.table = gtk.Table(2, 7)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)
        self.add_with_viewport(self.table)
        self.partlist = []
        # column headers
        i = 0
        for l in (_(" Partition "), _("Mount Point"), _("   Size   "),
                _("Mnt Opts"), _("Format"), _("File-system"),
                _("Fmt Opts")):
            lw = gtk.Button(l)
            self.table.attach(lw, i, i+1, 0, 1, yoptions=0)
            i += 1

        line = gtk.HSeparator()
        self.table.attach(line, 0, 7, 1, 2, yoptions=0)

        self.fs_liststore = gtk.ListStore(str)
        self.cellr = gtk.CellRendererText()
        for fs in install.filesystems:
            self.fs_liststore.append([fs])

    def clear(self):
        """Clear the partition table in preparation for switching to
        another disk drive.
        """
        # Remove old widgets
        for p in self.partlist:
            self.table.remove(p.devw)
            self.table.remove(p.mpw)
            self.table.remove(p.sizew)
            self.table.remove(p.moptw)
            self.table.remove(p.fmtw)
            self.table.remove(p.fstw)
            self.table.remove(p.foptw)
        # Forget the previous partitions
        self.partlist = []

    def addrow(self, partobj):
        """Add a row to the table corresponding to the partition object
        passed as argument.
        """
        ri = len(self.partlist) + 2
        self.partlist.append(partobj)
        self.table.resize(ri+1, 7)
        self.table.attach(partobj.devw, 0, 1, ri, ri+1, yoptions=0)
        self.table.attach(partobj.mpw, 1, 2, ri, ri+1, yoptions=0)
        self.table.attach(partobj.sizew, 2, 3, ri, ri+1, yoptions=0)
        self.table.attach(partobj.moptw, 3, 4, ri, ri+1, yoptions=0)
        self.table.attach(partobj.fmtw, 4, 5, ri, ri+1, xoptions=0, yoptions=0)
        self.table.attach(partobj.fstw, 5, 6, ri, ri+1, yoptions=0)
        self.table.attach(partobj.foptw, 6, 7, ri, ri+1, yoptions=0)

        partobj.fstw.set_model(self.fs_liststore)
        partobj.fstw.pack_start(self.cellr, True)
        partobj.fstw.add_attribute(self.cellr, 'text', 0)
        try:
            partobj.fstw.set_active(install.filesystems.index(
                    partobj.newformat))
        except:
            partobj.fstw.set_active(-1)

    def showtable(self):
        """To be called when the partition table has been completed.
        """
        if not self.partlist:
            self.table.resize(3, 7)
            notice = gtk.Label(_("No partitions available on this device"))
            self.table.attach(notice, 0, 7, 2, 3, yoptions=0)

        self.table.show_all()

        from doinstall_gui import Report, Progress
        self.output = Report()
        self.addWidget(self.output)

        self.progress = Progress()
        self.addWidget(self.progress, False)
        self.request_soon(self.run)

    def run(self):
        # need to disable forward button
        mainWindow.enable_forward(False)
        mainWindow.busy_on(False)

        self.ok = False
        if self.format():
            mountlist = install.mount()
            if mountlist:
                for m, p in mountlist:
                    self.output.report(_("Mounted partition %s at %s")
                            % (p, m))

                if (self.install() and install.unmount()):
                    self.output.report(_("Unmounted installation"
                            " partitions."))
                    self.output.report(_("\nInstallation completed"
                            " successfully."))
                    self.output.report(_("\nPress 'Forward' to continue"))
                    self.ok = True
                else:
                    self.output.report(_("\nInstallation failed"))
            else:
                self.output.report(_("Couldn't mount installation"
                        " partition(s)"))
        # need to reenable forward button
        mainWindow.busy_off(False)
        mainWindow.enable_forward(True)
        return self.stop_callback()

    def reinit(self):
        self.output.report(_("The installation has already been completed."
                " No further action is possible."))

    def format(self):


#        print "NOT FORMATTING"
#        return True

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

    def install(self):

#        print "NOT INSTALLING"
#        return True


        self.progress_count = 0
        self.progress_ratio = 1.0
        totalsize = 0
        self.output.report(_("Estimating installation size ..."))
        self.basesize = install.get_size()
        dlist = ["/bin", "/boot", "/etc", "/root", "/sbin", "/srv", "/lib",
                "/opt", "/home"]
        dlist += ["/usr/" + d for d in install.lsdir("/usr")]
        dlist.append("/var")

        self.system_size = 0
        partsizes = {}
        for d in dlist:
            gs = install.guess_size(d)
            partsizes[d] = gs
            self.system_size += gs

        self.output.report(_("Starting actual installation ...") + "\n---")
        self.progress.start()
        isize = self.basesize
        for d in dlist:
            #self.output.backline()
            self.output.report(_("--- Copying %s") % d)
            #print "cp", d, self.progress_ratio, totalsize, isize-self.basesize
            install.copyover(d, self.progress_cb)
            totalsize += partsizes[d]
            isize = install.get_size()
            self.progress_ratio = float(totalsize) / (isize - self.basesize)

        install.install_tidy()

        self.progress.ended()
        self.output.report(_("Copying of system completed."))
        self.output.report(_("Generating initramfs (this could take a while ...)"))
        install.mkinitcpio()
        self.output.report(_("Generating /etc/fstab"))
        return True

    def progress_cb(self):
        self.progress_count += 1
        if self.progress_count < 10:
            return
        self.progress_count = 0
        installed_size = install.get_size()
        frac = ((installed_size  - self.basesize) * self.progress_ratio
                / self.system_size)
        if (frac > 1.0):
            frac = 1.0
        self.progress.set(installed_size - self.basesize, frac)

    def forward(self):
        if self.ok:
            mainWindow.goto('grub')
        else:
            mainWindow.goto('error')


#################################################################

moduleName = 'InstallStart'
moduleDescription = _("Start the actual installation process")

