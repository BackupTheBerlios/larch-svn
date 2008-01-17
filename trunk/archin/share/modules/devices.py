# 2008.01.17

class Devices(Stage, gtk.TreeView):
    def stageTitle(self):
        return _("Select installation device")

    def getHelp(self):
        return _("Here you can choose to which of the disk(-like) devices"
                " you want to install Arch Linux.\n\n"
                "Select one of the devices"
                " and click on the 'Forward' button.\n\n"
                "To use partitions from more than one device you must"
                " select 'multiple' and click on the 'Forward' button."
                " You will be taken to the manual partitioning menu.")


    def __init__(self):
        gtk.TreeView.__init__(self)
        self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_VERTICAL)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Device"), renderer, text=0)
        self.append_column(column)
        column = gtk.TreeViewColumn(_("Size"), renderer, text=1)
        self.append_column(column)
        column = gtk.TreeViewColumn(_("Description"), renderer, text=2)
        self.append_column(column)
        self.liststore = gtk.ListStore(str, str, str)
        for d, s, n in install.devices:
            self.liststore.append((d, s, n))
        self.liststore.append((_("multiple"), "-", "-"))
        self.set_model(self.liststore)

        treeselection = self.get_selection()
        treeselection.select_path(0)

    def forward(self):
        selec = self.get_selection()
        m, r = selec.get_selected_rows()
        try:
            row = r[0][0]
        except:
            popupMessage(_("Please select an entry in the list."))
            return
        if (row == self.get_visible_range()[1][0]):
            install.setDevice(-1)
            mainWindow.goto('manualPart')
        else:
            install.setDevice(row)
            mainWindow.goto('partitions')


stages['devices'] = Devices
