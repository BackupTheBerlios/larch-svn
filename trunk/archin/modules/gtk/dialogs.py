#!/usr/bin/env python
#
# dialogs.py - popup dialogs for archin
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

def popupError(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin Error"))
    dialog.run()
    dialog.destroy()

def popupMessage(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin"))
    dialog.run()
    dialog.destroy()

def popupWarning(text, title=""):
    dialog = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
            title)
    dialog.format_secondary_markup(text)
    dialog.set_title(_("archin"))
    res = (dialog.run() == gtk.RESPONSE_YES )
    dialog.destroy()
    return res
