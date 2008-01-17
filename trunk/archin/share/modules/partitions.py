# partitions.py - select automatic or manual partitioning stage
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

class Partitions(Stage, gtk.VBox):
    def stageTitle(self):
        return _("Choose partitioning scheme")

    def getHelp(self):
        return _("Here you can choose which part(s) of the disk(-like)"
                " device to use for the Arch Linux installation.\n\n"
                "WARNING: If you have an operating system already installed"
                " on this drive which you wish to keep, you must choose"
                " 'expert' partitioning, unless the existing operating"
                " system is on the first partition ONLY, and uses the NTFS"
                " file-system (Windows).")


    def __init__(self):
        """Things could have changed if we return to this stage, so
        all the setting up is done in 'reinit'.
        """
        gtk.VBox.__init__(self)
        self.box = None
        self.reinit()

    def reinit(self):
        if self.box:
            self.remove(self.box)
        self.box = gtk.VBox()
        self.pack_start(self.box)

        dev = install.selectedDevice()
        dsizestr = install.selectedDeviceSizeString()

        label = gtk.Label(_("Total capacity of drive %s: %s") %
                (dev, dsizestr))
        self.box.pack_start(label)

        # Offer manual partitioning
        manual = gtk.RadioButton(None, _("Expert partitioning"))
        self.box.pack_end(manual)

        # Offer whole drive
        self.whole = gtk.RadioButton(manual, _("Use whole drive"))
        self.box.pack_end(self.whole)
        self.whole.set_active(True)

        # Conditional option, see below
        self.part2 = None

        # Info on drive and partitions (dev="/dev/sda", etc.):
        install.getDeviceInfo(dev)

        # Only offer to use rest (after first partition) if:
        #   (a) part1 is NTFS, and (b) disk > min size
        min = 1e10
        if install.p1size and (install.dsize > min):
            val = float(install.dsize) / 2e9
            valmax = float(install.p1size) / 1e9 - 0.5
            if ( valmax < val):
                val = valmax
            self.ntfsinfo = install.getNTFSinfo(dev+"1")
            valmin = self.ntfsinfo[3] / 1e9 + 0.1

            if (valmin >= valmax):
                popupMessage(_("The option to reduce the size of the first"
                        " partition is not available because it is too full."))
                return

            # Offer to keep first partition and use rest of drive for Arch
            self.part2 = gtk.RadioButton(manual,
                     _("Keep existing operating system"
                    " and use rest of drive for Arch Linux"))
            self.box.pack_end(self.part2)
            self.part2.connect("toggled", self.part2toggled)

            label1 = gtk.Label(_("If you wish to retain the operating system"
                    " currently installed on the first partition, you have"
                    " here the option of shrinking it,"
                    " to create enough space for Arch Linux"))
            label1.set_line_wrap(True)
            self.box.pack_start(label1)

            self.sframe = gtk.Frame()
            adjlabel = gtk.Label(_("Set new size of NTFS partition (GB)"))
            self.adj = gtk.Adjustment(val, valmin, valmax,
                    step_incr=0.1, page_incr=1.0)
            hscale = gtk.HScale(self.adj)
            freelabel = gtk.Label(_("Free space (GB):"))
            self.freesize = gtk.Entry(10)
            self.freesize.set_editable(False)

            vbox = gtk.VBox()
            hbox = gtk.HBox()
            hbox.pack_end(self.freesize, False)
            hbox.pack_end(freelabel, False)
            self.shrinkbox = gtk.VBox()
            self.shrinkbox.pack_start(adjlabel)
            self.shrinkbox.pack_start(hscale)
            vbox.pack_start(self.shrinkbox)
            vbox.pack_start(hbox)

            self.adj.connect("value_changed", self.resize_value)

            self.sframe.add(vbox)
            self.box.pack_start(self.sframe)

            self.shrink = gtk.CheckButton(_("Shrink NTFS partition"))
            self.sframe.set_label_widget(self.shrink)
            self.shrink.connect("toggled", self.shrink_check_cb)
            self.shrink.set_active(True)
            self.shrink.set_active(False)

            self.part2.set_active(True)
            if ( ( (install.dsize-install.p1size) <= (min/2) ) or
                    ( install.p1size > (install.dsize/2) ) ):
                # Activate shrinking by default
                self.shrink.set_active(True)

    def shrink_check_cb(self, widget, data=None):
        on = widget.get_active()
        self.shrinkbox.set_sensitive(on)
        self.resize_value(self.adj)

    def resize_value(self, widget, date=None):
        ws = widget.get_value()
        size = float(install.dsize)/1e9
        if self.shrink.get_active():
            size -= ws
        else:
            size -= float(install.p1size)/1e9
        self.freesize.set_text("%8.1f" % size)

    def part2toggled(self, widget, date=None):
        on = widget.get_active()
        self.sframe.set_sensitive(on)
        if on:
            self.resize_value(self.adj)


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
                        self.reinit()
                        return

                else:
                    self.reinit()
                    return

            else:
                part2start = install.p1end + 1

            install.setPart(part2start)
            mainWindow.goto('autoPart')

        elif self.whole.get_active():
            # Use whole drive
            install.setPart(0)
            mainWindow.goto('autoPart')

        else:
            # Manual partitioning
            install.setPart(None)
            mainWindow.goto('manualPart')


stages['partitions'] = Partitions
