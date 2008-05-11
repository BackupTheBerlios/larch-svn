# welcome.py - first - 'welcome' - stage
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
# 2008.05.11

from stage import Stage

class Widget(Stage):
    def __init__(self):
        Stage.__init__(self, moduleDescription)
        self.addLabel(_('This will install Arch Linux'
                ' from this "live" system on your computer.'
                ' This program was written'
                ' for the <i>larch</i> project:\n'
                '       http://larch.berlios.de\n'
                '\nIt is free software,'
                ' released under the GNU General Public License.\n\n') +
                'Copyright (c) 2008   Michael Towers')

    def getHelp(self):
        return _("Click on the 'OK' button to start.")

    def forward(self):
        return 0


#################################################################

moduleName = 'Welcome'
moduleDescription = _('Welcome to <i>larchin</i>')

