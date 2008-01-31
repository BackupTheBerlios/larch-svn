# doinstall_gui.py - extra widgets for the installation stage
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

import gtk

class Report(gtk.ScrolledWindow):
    """
    """
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        view = gtk.TextView()
        view.set_editable(False)
        #view.set_wrap_mode(gtk.WRAP_WORD)
        self.add(view)
        self.show()
        view.show()

        self.reportbuf = view.get_buffer()

    def report(self, text):
        self.reportbuf.insert(self.reportbuf.get_end_iter(), text+'\n')
        while gtk.events_pending():
            gtk.main_iteration(False)
