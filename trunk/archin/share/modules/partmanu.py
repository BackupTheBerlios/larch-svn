# 2008.01.16


class ManuPart(Stage, gtk.VBox):
    def stageTitle(self):
        return _("Edit installation partitions manually")

    def getHelp(self):
        return _("Here you can choose a partitioning tool and/or disk(-like)"
                " device in order to prepare your system to receive an"
                " Arch Linux installation.\n\n"
                "'cfdisk' is a console based tool which should always be"
                " available. It must be started with the name of the"
                " device on which it is to be used.\n\n"
                "'gparted' is a fancy gui-tool which can do much more,"
                " including resizing partitions, but it  may not always"
                " be available. The device to be edited can be selected"
                " from within the program.")


    def __init__(self):
        gtk.VBox.__init__(self)

        dev = install.selectedDevice()

        # Offer gparted - if available
        if (install.gparted_available() == ""):
            self.gparted = gtk.RadioButton(None, _("Use gparted (recommended)"))
            self.pack_start(self.gparted)
            self.gparted.set_active(True)
        else:
            self.gparted = None
        buttongroup = self.gparted

        # Offer cfdisk on each available disk device
        self.cfdisklist = []
        for d, s, t in install.devices:
            b = gtk.RadioButton(buttongroup, _("Use cfdisk on %s") % d)
            self.pack_start(b)
            buttongroup = b
            if (d == dev) and not self.gparted:
                b.set_active(True)
            self.cfdisklist.append(b)

        # Offer 'use existing partitions/finished'
        self.done = gtk.RadioButton(buttongroup, _("Use existing partitions /"
                " finished editing partitions"))
        self.pack_end(self.done)


    def forward(self):
        if (self.gparted and self.gparted.get_active()):
            install.gparted()
            self.reinit()

        elif self.done.get_active():
            mainWindow.goto('partSelect')

        else:
            i = 0
            for b in self.cfdisklist:
                if b.get_active():
                    install.cfdisk(i)
                    break
                i += 1
            self.reinit()


stages['manualPart'] = ManuPart
