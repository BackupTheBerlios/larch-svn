# rootpw.py - set root password for installed system
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
# 2008.04.17

class Rootpw(Stage):
    def stageTitle(self):
        return _("Set root password"))

    def labelR(self):
        return gtk.STOCK_OK

    def __init__(self):
        Stage.__init__(self)
        self.addLabel(_("Enter new root password:"), align='left')
        self.pw1 = gtk.Entry()
        self.pw1.set_visibility(False)
        self.addWidget(self.pw1)

        self.addLabel(_("Reenter new root password:"), align='left')
        self.pw2 = gtk.Entry()
        self.pw2.set_visibility(False)
        self.addWidget(self.pw2)

    def getHelp(self):
        return _("You should enter a hard-to-guess password for the root"
                " account on the newly installed system. Use a mixture of"
                " letters, digits and other characters. The password may"
                " be left empty, but that will make it more difficult to"
                " make use of the root account for system administration.\n\n"
                "If you are not a linux expert, you are strongly advised"
                " not to lose/forget the password you set here.")

    def forward(self):
        # Check entered passwords are identical

        pw = self.pw1.get_text()
        if (pw != self.pw2.get_text()):
            popupMessage(_("The passwords are not identical,\n"
                    "  Please try again.")):

        # Set the password
        elif install.set_rootpw(pw):
            mainWindow.goto('end')
            return

        self.reinit()

#################################################################

stages['rootpw'] = Rootpw
