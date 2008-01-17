# stage.py - base class for stages of the installer
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

import gtk

class Stage:
    def __init__(self, vbox=None):
        if vbox:
            self.optionbox = vbox
        else:
            self.optionbox = self
        self.options = {}
        self.option0 = None

    def labelL(self):
        return gtk.STOCK_GO_BACK

    def labelR(self):
        return gtk.STOCK_GO_FORWARD

    def reinit(self):
        return

    def stageTitle(self):
        return _("Undocumented stage")

    def getHelp(self):
        return _("Sorry, I'm afraid there is at present no information"
                " for this stage.")

    def help(self):
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
        dialog.set_markup("<b>%s</b>" % self.stageTitle())
        dialog.format_secondary_markup(self.getHelp())
        dialog.set_title(_("archin Help"))
        dialog.run()
        dialog.destroy()

    def addOption(self, name, label, default=False):
        b = gtk.RadioButton(self.option0, label)
        self.options[name] = b
        self.optionbox.pack_start(b)
        self.option0 = b
        if default:
            b.set_active(True)
        return b

    def getSelectedOption(self):
        for n, b in self.options.items():
            if b.get_active():
                return n
        return None
