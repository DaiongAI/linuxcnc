#!/usr/bin/env python
# GladeVcp Widget - DRO label widget
# This widgets displays linuxcnc axis position information.
#
# Copyright (c) 2012 Chris Morley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys,os
import math
import linuxcnc
from PyQt4 import QtCore, QtGui
from qtvcp import qt_glib

# we put this in a try so there is no error in the glade editor
# linuxcnc is probably not running then 
try:
    INIPATH = os.environ['INI_FILE_NAME']
except:
    pass

class Lcnc_DROLabel(QtGui.QLabel):
    def __init__(self, parent = None):
        QtGui.QLabel.__init__(self,parent)
        self.gstat = qt_glib.GStat()
        self.emc = linuxcnc
        self.display_units_mm=0
        self.machine_units_mm=0
        self.unit_convert=[1]*9
        self.diameter = False
        self.reference_type = 0
        self.joint_number = 0
        self.mm_text_template = '%10.3f'
        self.imperial_text_template = '%9.4f'
        self.setText('--------------')

        try:
            self.inifile = self.emc.ini(INIPATH)
            # check the ini file if UNITS are set to mm"
            # first check the global settings
            units=self.inifile.find("TRAJ","LINEAR_UNITS")
            if units==None:
                # else then the X axis units
                units=self.inifile.find("AXIS_0","UNITS")
        except:
            units = "inch"
        # set up the conversion arrays based on what units we discovered
        if units=="mm" or units=="metric" or units == "1.0":
            self.machine_units_mm=1
            conversion=[1.0/25.4]*3+[1]*3+[1.0/25.4]*3
        else:
            self.machine_units_mm=0
            conversion=[25.4]*3+[1]*3+[25.4]*3
        self.set_machine_units(self.machine_units_mm,conversion)
        # get position update from gstat every 100 ms
        self.gstat.connect('current-position',self.update)

    def update(self,widget,absolute,relative,dtg):
        if self.display_units_mm != self.machine_units_mm:
            absolute = self.convert_units(absolute)
            relative = self.convert_units(relative)
            dtg = self.convert_units(dtg)

        if self.display_units_mm:
            tmpl = lambda s: self.mm_text_template % s
        else:
            tmpl = lambda s: self.imperial_text_template % s
        if self.diameter:
            scale = 2.0
        else:
            scale = 1
        if self.reference_type == 0:
            self.setText(tmpl(absolute[self.joint_number]*scale))
        elif self.reference_type == 1:
            self.setText(tmpl(relative[self.joint_number]*scale))
        elif self.reference_type == 2:
            self.setText(tmpl(dtg[self.joint_number]*scale))
        return True

    def set_machine_units(self,u,c):
        self.machine_units_mm = u
        self.unit_convert = c

    def convert_units(self,v):
        c = self.unit_convert
        return map(lambda x,y: x*y, v, c)

    def set_to_inch(self):
        self.display_units_mm = 0

    def set_to_mm(self):
        self.display_units_mm = 1

    def set_to_diameter(self):
        self.diameter = True

    def set_to_radius(self):
        self.diameter = False

# property getter/setters

    # JOINT Number
    def setjoint_number(self, data):
        self.joint_number = data
    def getjoint_number(self):
        return self.joint_number
    def resetjoint_number(self):
        self.joint_number = 0
    Qjoint_number = QtCore.pyqtProperty(int, getjoint_number, setjoint_number, resetjoint_number)

    # user system Number
    def setreference_type(self, data):
        self.reference_type = data
    def getreference_type(self):
        return self.reference_type
    def resetreference_type(self):
        self.reference_type = 0
    Qreference_type = QtCore.pyqtProperty(int, getreference_type, setreference_type, resetreference_type)

# for testing without editor:
def main():
    import sys
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)
    widget = Lcnc_DROLabel()
    widget.show()
    sys.exit(app.exec_())
if __name__ == "__main__":	
    main()


