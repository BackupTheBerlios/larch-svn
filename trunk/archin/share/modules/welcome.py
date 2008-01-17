# 2008.01.16

class Welcome(Stage, gtk.Label):
    def stageTitle(self):
        return ('<i>archin</i>: %s' % _("Install Arch Linux"))

    def __init__(self):
        gtk.Label.__init__(self)
        self.set_justify(gtk.JUSTIFY_FILL)
        self.set_line_wrap(True)
        self.set_use_markup(True)
        self.set_label(_('Welcome to <i>archin</i>. This will install'
                ' Arch Linux on your computer. This program was written'
                ' for the <i>larch</i> project:\n'
                '       http://larch.berlios.de\n'
                '\nIt is free software,'
                ' released under the GNU General Public License.\n\n') +
                'Copyright (c) 2008   Michael Towers')

    def getHelp(self):
        return _("Click on the 'Forward' button to start.")

    def forward(self):
        install.getDevices()
        devs = install.devices
        if not devs:
            popupError("No disk(-like) devices were found,"
                    " so Arch Linux can not be installed on this machine")
            end()
        if (len(devs) == 1):
            install.setDevice(0)
            mainWindow.goto('partitions')
        else:
            mainWindow.goto('devices')


stages['welcome'] = Welcome
