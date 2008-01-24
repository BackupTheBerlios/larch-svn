# selpart_gui.py - extra widgets for the manual partition selection stage
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

import gtk

class SelTable(gtk.Table):
    """This widget presents a list of available partitions for
    allocation in the new system.
    """
    def __init__(self, master):
        gtk.Table.__init__(self)
        self.rows = []
# Maybe there should be column headers?

    def renew(self, partdict):
        # First remove old widgets
        for r in self.rows:
            for w in r[1:]:
                self.remove(w)
        self.rows = []

        parts = partdict.keys()
        parts.sort()
        self.resize(len(parts), 5)
        for p in parts:
            devw = gtk.Label(p)
            pinfo = partdict[p]
            mpw = SelPartMountPoint(pinfo[2])
            sizew = gtk.Label("%8.1f GB" % (float(pinfo[0]) / 1000))
# and so on


class SelDevice(gtk.HBox):
    """This widget allows selection of the device on which partitions are
    to be allocated to mountpoints, formatted, etc.
    """
    def __init__(self, master, devices):
        self.master = master
        assert False, 'NYI'
        label = gtk.Label(_("Configuring partitions on drive ")
        combo = gtk.combo_box_new_text()
        for d in devices:
            combo.append_text(d.rstrip('-'))
        combo.connect('changed', self.newdevice)

    def newdevice(self, widget, data=None):
        self.master.setDevice(widget.get_active_text())

#?
def SelOptionDialog(fopts, ftext, mopts, mtext):
    assert False, 'NYI'


