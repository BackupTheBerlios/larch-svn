#!/usr/bin/env python
#
# luser.py  - a gui for basic user management under linux,
#                 a front-end for the commands useradd, usermod, userdel
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
# 2008.04.06

import gtk
import os, pwd, grp
from subprocess import Popen, PIPE


# Not at all ready yet, I'm just modifying the larchquit code first to
# get a gui framework ...

# If not started as root, it should probably only show the groups and
# allow the password to be changed, but it might be reasonable for it
# to allow everything, but ask for the root password if anything other
# than changing the current user's password is to be done (using pexpect
# to run shell stuff as root).



class Luser(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        #self.set_default_size(400,300)
        self.connect("destroy", actions.exit)
        self.set_border_width(3)

        notebook = gtk.Notebook()
        self.add(notebook)
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show_tabs = True
        notebook.show_border = False

        self.users = Users()
        notebook.append_page(self.users, gtk.Label(_("Users")))
        #notebook.append_page(Configure(), gtk.Label(_("Configure")))
        notebook.append_page(Help(), gtk.Label(_("Help")))
        notebook.append_page(About(), gtk.Label(_("About")))

        notebook.set_current_page(0)

    def mainLoop(self):
        self.show_all()
        gtk.main()

    def getUsers(self):
        """Return a list of 'normal' users, i.e. those with a home
        directory in /home and a login shell (ending with 'sh').
        """
        return [u[0] for u in pwd.getpwall()
                if (u[5].startswith('/home/') and u[6].endswith('sh'))]

    def getGroups(self):
        """Return a list of 'normal' groups, i.e. those with ... ?
        """
        return [g[0] for g in grp.getgrall()]

    def getUserGroups(self, user):
        """Return the list of groups for the given user.
        """
        return [gu[0] for gu in grp.getgrall() if user in gu[3]]

    def getUserInfo(self, user):
        """Return (uid, gid) for the given user.
        """
        return pwd.getpwnam(user)[2:4]

#WHat about the primary group????
# uid and gid are 3rd and 4th fields in passwd
# root is also a special case: can only set password



class Help(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.view = gtk.TextView()
        self.view.set_editable(False)
        #view.set_wrap_mode(gtk.WRAP_WORD)
        sw.add(self.view)
        self.add(sw)
        self.view.show()

        self.reportbuf = self.view.get_buffer()


class About(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(5)
        box = gtk.VBox()
        box.set_border_width(10)
        label = gtk.Label()
        label.set_line_wrap(True)
        #label.set_alignment(0.0, 0.5)
        label.set_markup(_('<i>luser</i> is a simple gui front-end for'
                ' the command line user management programs. It was'
                ' designed for <i>larch</i> \'live\' systems but should'
                ' work on most linux systems.\n'
                'To keep it simple it only allows adding and deleting users,'
                ' changing their passwords, and changing their group'
                ' memberships.\n\n'
                'This program was written for the <i>larch</i> project:\n'
                '       http://larch.berlios.de\n'
                '\nIt is free software,'
                ' released under the GNU General Public License.\n\n') +
                'Copyright (c) 2008   Michael Towers')
        box.pack_start(label)
        self.add(box)


class Configure(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        self.set_border_width(10)
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_markup(_('<b>Not Yet implemented</b>'))
        self.add(label)

--------------------------------------------------------------------
class Users(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, spacing=20)
        self.set_border_width(10)

        mainbox = gtk.HBox(spacing=5)
        buttonbox = gtk.HBox(spacing=5)

        leftbox = gtk.VBox(spacing=5)

        grouplist = CheckList()

        mainbox.pack_start(leftbox)
        mainbox.pack_start(grouplist)




class CheckList(gtk.ScrolledWindow):
    def __init__(self, columnwidth=100):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.set_size_request(columnwidth, -1)

        self.treeview = gtk.TreeView()
        self.liststore = gtk.ListStore(str, bool, bool)
        # create CellRenderers to render the data
        celltoggle = gtk.CellRendererToggle()
        #celltoggle.set_property('activatable', True)
        celltext = gtk.CellRendererText()
        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn(_("Groups"))
        self.tvcolumn.pack_start(celltoggle, expand=False)
        self.tvcolumn.add_attribute(celltoggle, 'active', 1)
        self.tvcolumn.add_attribute(celltoggle, 'activatable', 2)
        self.tvcolumn.pack_start(celltext, expand=True)
        self.tvcolumn.add_attribute(celltext, 'text', 0)
        # add column to treeview
        self.treeview.append_column(self.tvcolumn)
        # place treeview in scrolled window
        self.add(self.treeview)



    def setGroups(self, user):
        """Write the list of groups to the list, and set toggles
        according to the membership of the current user.
        """
        groups = gui.getGroups()
        usergroups = gui.getUserGroups(user)
        uid, gid = gui.getUserInfo(user)
        self.liststore.clear()
        for g in groups:
            enable = (g != gid) and (g not in ('root', 'bin', 'daemon',
                    'sys', 'adm'))
            self.liststore.append(g, g in usergroups, enable)






###############
GROUPS:
Mitglieder hinzufügen

root@sonne> gpasswd -a user fibel
Adding user user to group fibel

Mitglieder entfernen

root@sonne> gpasswd -d user fibel
Removing user user from group fibel


But usermod can also set / add user's groups
######################



-------------------------------------------------------------

class Actions:
    def __init__(self):
        print "NYI"

    def exit(self, widget=None, data=None):
        gtk.main_quit()


def error(message):
    md = gtk.MessageDialog(flags=gtk.DIALOG_MODAL |
            gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_CLOSE, message_format=message)
    md.run()

if __name__ == "__main__":
    import sys
    import __builtin__
    def tr(s):
        return s
    __builtin__._ = tr

    actions = Actions()
    gui = Luser()
    gui.mainLoop()
