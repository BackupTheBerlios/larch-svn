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
# 2008.04.08

import gtk
import os, pwd, grp
from subprocess import Popen, PIPE, STDOUT

# For switching to root.
import pexpect

# Not quite ready yet ...

# If not started as root, it will ask for the root password if necessary
# (NYI!)

class Luser(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        #self.set_default_size(400,300)
        self.connect("destroy", actions.exit)
        self.set_border_width(3)

        self.currentUser = None
        self.password = None

        notebook = gtk.Notebook()
        self.add(notebook)
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.show_tabs = True
        notebook.show_border = False

        self.users = Users(self.getUsers() + ['root'])
        notebook.append_page(self.users, gtk.Label(_("Users")))
        #notebook.append_page(Configure(), gtk.Label(_("Configure")))
        notebook.append_page(Help(), gtk.Label(_("Help")))
        notebook.append_page(About(), gtk.Label(_("About")))

        notebook.set_current_page(0)

    def mainLoop(self):
        self.show_all()
        gtk.main()

    def rootrun(self, cmd):
        """Run the given command as 'root'.
        Return a pair (completion code, output).
        """
        # If not running as 'root', use pexpect to do su and run the command
        if (os.getuid() == 0):
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            o = p.communicate()[0]
            return (p.returncode, o)
        else:
            if not self.password:
                self.password = popupRootPassword()
            child = pexpect.spawn("su -c '%s'" % cmd)
            child.expect(':')
            child.sendline(self.password)
            child.expect(pexpect.EOF)
            o = child.before.strip()
            return (0 if (o == '') else 1, o)

    def changeUser(self, user):
        if self.pending(user):
            self.currentUser = user
            self.users.setRoot(user == 'root')
            self.users.grouplist.setGroups(user)
        else:
            self.users.resetUser(self.currentUser)

    def pending(self, user=None):
        """Handle pending changes to group membership for the current user.
        Should be called when the user is switched and when quitting the
        program.
        """
        if ((self.currentUser in self.getUsers()) and
                (self.currentUser != user)):

            nglist = self.users.grouplist.getNewGroups()
            if (self.getUserGroups(self.currentUser) != nglist):
                # Changes were requested, popup an apply confirmation dialog

                if confirm(_("You have specified changes to the group"
                        " memberships of user '%s'.\n\n"
                        "Should these be applied?")
                         % self.currentUser):

                    glist = reduce((lambda a,b: a+','+b if a else b), nglist)
                    ccode, op = self.rootrun('usermod -G %s %s' %
                            (glist, self.currentUser))
                    if (ccode != 0):
                        error(_("The group memberships of user '%s'"
                                " could not be changed. Here is the system"
                                " message:\n\n %s") % (self.currentUser, op))
                        return False
        return True

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
        """Return the list of supplemental groups for the given user.
        """
        return [gu[0] for gu in grp.getgrall() if user in gu[3]]

    def getUserInfo(self, user):
        """Return (uid, gid) for the given user.
        """
        return pwd.getpwnam(user)[2:4]


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


class Users(gtk.HBox):
    def __init__(self, userlist):
        gtk.HBox.__init__(self, spacing=20)
        self.set_border_width(10)

        leftbox = gtk.VBox(spacing=5)

        self.grouplist = CheckList()

        self.pack_start(leftbox)
        self.pack_end(self.grouplist)

        # leftbox:
        #    user select combobox
        self.usel = SelectUser()
        self.usel.setUsers(userlist)
        leftbox.pack_start(self.usel, False)

        #    add user button -> user name + password popup
        newuser = gtk.Button(_("New user"))
        newuser.connect('clicked', self.newUser)
        leftbox.pack_start(newuser, False)

        #    change password button -> password popup
        newpw = gtk.Button(_("Change password"))
        newpw.connect('clicked', self.newPass)
        leftbox.pack_start(newpw, False)

        #    remove user button -> are you sure confirmation
        self.delete = gtk.Button(_("Remove this user"))
        self.delete.connect('clicked', self.removeUser)
        leftbox.pack_start(self.delete, False)

        quit = gtk.Button(stock=gtk.STOCK_QUIT)
        quit.connect('clicked', actions.exit)
        leftbox.pack_end(quit, False)

    def setRoot(self, root):
        """If the selected user is 'root', editing of the groups and
        deleting the user should be diabled.
        """
        self.grouplist.setEnabled(not root)
        self.delete.set_sensitive(not root)

    def resetUser(self, user):
        self.usel.select(user)

    def newUser(self, widget, data=None):
        print "newUser NYI"


    def newPass(self, widget, data=None):
        print "newPass NYI"


    def removeUser(self, widget, data=None):
        if confirm(_("Do you really want to remove user '%s', including"
                " the home directory, i.e. losing all the data contained"
                " therein?")
                 % self.currentUser):

            ccode, op, op2 = self.rootrun('userdel -r %s' % self.currentUser)
            if (ccode != 0):
                error(_("User '%s' could not be removed. Here is the system"
                        " message:\n\n %s") % (self.currentUser, op2))




class SelectUser(gtk.ComboBox):
    def __init__(self):
        gtk.ComboBox.__init__(self)
        self.blocked = False
        self.list = gtk.ListStore(str)
        self.set_model(self.list)
        cell = gtk.CellRendererText()
        self.pack_start(cell)
        self.add_attribute(cell, 'text', 0)
        self.connect('changed', self.changed_cb)

    def setUsers(self, ulist):
        self.list.clear()
        for u in ulist:
            self.list.append([u])

    def changed_cb(self, widget, data=None):
        if self.blocked:
            self.blocked = False
            return
        i = self.get_active()
        u = self.list[i][0]
        gui.changeUser(u)

    def select(self, user):
        i = 0
        for u in self.list:
            if (u[0] == user):
                self.blocked = True
                self.set_active(i)
                break
            i += 1


# This should only be enabled(sensitive) when run as root and selecteduser!=root
class CheckList(gtk.ScrolledWindow):
    def __init__(self, columnwidth=100):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.set_size_request(columnwidth, -1)

        self.treeview = gtk.TreeView()
        self.liststore = gtk.ListStore(str, bool, bool)
        self.treeview.set_model(self.liststore)
        # create CellRenderers to render the data
        celltoggle = gtk.CellRendererToggle()
        #celltoggle.set_property('activatable', True)
        celltoggle.connect( 'toggled', self.toggled_cb)
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

    def toggled_cb(self, widget, path, data=None):
        self.liststore[path][1] = not self.liststore[path][1]

    def setEnabled(self, enable):
        self.treeview.set_sensitive(enable)

    def setGroups(self, user):
        """Write the list of groups to the list, and set toggles
        according to the membership of the current user.
        """
        groups = gui.getGroups()
        usergroups = gui.getUserGroups(user)
        uid, gid = gui.getUserInfo(user)
        self.gidnm = grp.getgrgid(gid)[0]
        self.liststore.clear()
        for g in groups:
            if (g == self.gidnm):
                self.liststore.append([g, True, False])
            else:
                enable = (g not in ('root', 'bin', 'daemon',
                        'sys', 'adm'))
                self.liststore.append([g, g in usergroups, enable])

    def getNewGroups(self):
        """Return the list of groups for the present user according to
        the checklist.
        """
        return [ r[0] for r in self.liststore
                        if (r[1] and (r[0] != self.gidnm))]




###############
#GROUPS:
#Mitglieder hinzufuegen

#root@sonne> gpasswd -a user fibel
#Adding user user to group fibel

#Mitglieder entfernen

#root@sonne> gpasswd -d user fibel
#Removing user user from group fibel


#But usermod can also set / add user's groups
######################




class Actions:
    def __init__(self):
        print "Actions NYI"

    def exit(self, widget=None, data=None):
        gui.pending()
        gtk.main_quit()

def popupRootPassword():
    # Maybe once it has been received it should be tested before returning it?
    print "root password NYI"
    return ""

def error(message):
    md = gtk.MessageDialog(flags=gtk.DIALOG_MODAL |
            gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_CLOSE, message_format=message)
    md.run()
    md.destroy()

def confirm(message):
    md = gtk.MessageDialog(flags=gtk.DIALOG_MODAL |
            gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_YES_NO, message_format=message)
    val = md.run()
    md.destroy()
    return (val == gtk.RESPONSE_YES)

if __name__ == "__main__":
    import sys
    import __builtin__
    def tr(s):
        return s
    __builtin__._ = tr

    actions = Actions()
    gui = Luser()
    gui.mainLoop()
