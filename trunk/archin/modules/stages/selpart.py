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
        from selpart_gui import SelTable, SelOptionDialog
        self.table_widget = SelTable
        self.option_dialog = SelOptionDialog
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
                    pinfo = [None, None, False, "#"]
                # pxinfo has the form: [size (MB), existing fstype,
                #       mount-point, new fstype, format, flags]
                pxinfo = [size, fstype] + pinfo
                self.parts[p] = pxinfo
                self.table.addPart(p, pxinfo)

    def ismounted(self, part):
        return re.search(r'^%s ' % part, self.mounts, re.M)

    def set_default_format_flags(self, p, fs):
        flags = '#'
        flist = self.format_flags(fs)
        if flist:
            for text, flag, on in flist:
                if on:
                    flags += flag
        mflags = self.parts[p][5].split('#')[0]
        self.parts[p][5] = mflags + flags


    def format_cb(self, p, on):
        self.parts[p][4]= on
        self.table.enable_fstype(p, on)
        if on:
            newfs = self.parts[p][1]
            if not newfs:
                newfs = 'ext3'
            self.parts[p][3] = newfs
            self.set_default_format_flags(p, newfs)
            self.table.set_fstype(p, newfs)

        else:
            self.table.set_fstype(p, self.parts[p][1])
            self.parts[p][3] = None

    def fstype_cb(self, p, fstype):
        # set default mount options
        flags = ''
        mlist = self.mount_flags(fs)
        if mlist:
            for text, flag, on in mlist:
                if on:
                    flags += flag
        self.parts[p][5] = flags + '#'

        if self.parts[p][4]:
            # if formatting
            self.parts[p][3] = fstype
            self.set_default_format_flags(p, fstype)
#        else:
#            self.parts[p][3] = None

    def options_cb(self, p):
        """Build a popup dialog containing the available options.
        """
        fopts = []
        flags = self.parts[p][5]
        if self.parts[p][4]:
            # Options only available if format box is checked
            fl = self.format_flags(self.parts[p][3])
            if fl:
                for desc, flag, on in fl:
                    fopts += (desc, flag, flag in flags)

        mopts = []
        if self.parts[p][2]:
            # Options only available if mount-point is set
            fl = self.mount_flags(self.parts[p][3])
            if fl:
                for desc, flag, on in fl:
                    mopts += (desc, flag, flag in flags)

        newopts = self.option_dialog(fopts,
                _("The following formatting options are available"),
                mopts,
                _("The following mount options are available"))
        self.parts[p][5] = newopts

    def device_cb(self, dev):
        self.save_settings()
        self.setDevice(dev)





    def save_settings(self):
        # Any partitions with format and/or mount-point need to be entered
        # into the (install) partitions set. All the others should be
        # removed if they are already in that set.
        assert False, "NYI"





    def format_flags(self, fstype):
        """Return a list of available format flags for the given
        file-system type.
        """
        # At the moment there is only an entry for 'ext3'
        return { 'ext3' : [ (_("disable boot-time checks"), 'd', True),
                            (_("directory indexing"), 'i', True),
                            (_("full journal"), 'f', False) ],
                }.get(fstype)

    def mount_flags(self, fstype):
        """Return a list of available mount (/etc/fstab) flags for the
        given file-system type.
        """
        # At the moment there are just these two flags
        flg = [ (_("noatime"), 'T', True),
                (_("noauto"), 'A', False) ]

        # And nothing file-system specific
        return flg



    def forward(self):
        sel = self.getSelectedOption()
        if (sel == 'done'):
            # prepare and process info
            #...
            # ... install.defPart("%s%d" % (dev, partno), '/home')

            mainWindow.goto('install')
            return



stages['partSelect'] = SelPart
