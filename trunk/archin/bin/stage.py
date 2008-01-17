import gtk

class Stage:
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
