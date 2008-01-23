#!/usr/bin/env python
#
# archin - A hard-disk installer for Arch Linux and larch
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

# Add a Quit button?

import os, sys

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("%s/modules" % basedir)
sys.path.append("%s/modules/gtk" % basedir)

from install import installClass
from archinmain import Archin

def end():
    print "Exiting"
    quit()

if (__name__ == "__main__"):
    import __builtin__
    def tr(s):
        return s
    __builtin__._ = tr

    import sys
    if (len(sys.argv) == 1):
        target = None
    elif (len(sys.argv) == 2):
        target = sys.argv[1]
    else:
        print "ERROR: too many arguments. Usage:"
        print "          archin.py [target-address]"
        sys.exit(1)

    __builtin__.basePath = basedir
    __builtin__.stages = {}
    __builtin__.mainWindow = Archin()
    __builtin__.install = installClass(target)
    mainWindow.goto('welcome')
    mainWindow.mainLoop()
