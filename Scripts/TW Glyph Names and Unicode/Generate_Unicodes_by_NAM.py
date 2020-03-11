#FLM: Generate Unicodes by NAM
# Python script for FontLab 7
# By Adam Twardoch, 2020-03-14
# Licensed at your choice under:
# - CC-0 (public domain)
# - MIT license, Copyright (c) 2020 Adam Twardoch

from __future__ import print_function, unicode_literals
import os.path
import re
import datetime
import fontlab as fl6
import fontgate as fgt
from PythonQt import QtCore, QtGui

__version__ = '0.2'
app_name = 'Generate Unicode by NAM'

def updateFont(f = None):
    f = f if f else CurrentFont()
    f.update()
    #lf = fl6.flPackage(f)
    #fl6.flItems.notifyPackageContentUpdated(lf.id)
    fl6.Update(f)

def assignUnicodes(g, us):
    # ideally this should be done via
    # g.unicodes = us
    # but casting Python lists to fg is extremely slow
    for u in g.unicodes:
        g.killUnicode(u)
    for u in us:
        g.addUnicode(u)

class fontGlyphNameUnicodes(object):

    def __init__(self, f = None):
        self.n2u = {}
        self.f = f if f else CurrentFont()

    def readFromFont(self, f = None):
        f = f if f else self.f
        self.n2u = {}
        for g in f.glyphs:
            self.n2u[g.name] = g.unicodes

    def _parseNamFile(self, namFile):
        reNAM = re.compile(r"^0x(?P<UNI>[A-Fa-f0-9]{4,5})\s+(?P<type>[>!]*)(?P<name>[A-Za-z0-9_\.-]+)")
        n2u = {}
        for l in namFile.readlines():
            m = reNAM.match(l)
            if m:
                n = m.group('name')
                u = int(m.group('UNI'), 16)
                t = m.group('type')
                n2u[n] = n2u.get(n, []) + [u]
        return n2u

    def readFromNamPath(self, namPath):
        with open(namPath, 'r') as namFile:
            self.n2u = self._parseNamFile(namFile)

    def writeToNamPath(self, namPath, f = None):
        f = f if f else self.f
        self.readFromFont(f)
        u2n = {}
        for n, us in self.n2u.items():
            for u in us:
                u2n[u] = n
        us = sorted(u2n.keys())

        namPrefix = f.info.openTypeOS2VendorID
        namFontName = f.info.postscriptFullName
        namDate = str(datetime.date.today())
        namFontPath = f.path

        with open(namPath, 'w') as t:
            t.write("%sFONTLAB NAMETABLE: [%s] %s %s\n" % ('%%', namPrefix, namFontName, namDate))
            t.write("%s Made from %s\n" % ('%', namFontPath))
            for u in us:
                t.write("0x%04X %s\n" % (u, u2n[u]))

    def writeToFont(self, f = None, keepUnicodes = True, flagModified = None):
        print("KEEPUNI %s" % keepUnicodes)
        f = f if f else self.f
        mods = 0
        for g in f.glyphs:
            n = g.name
            mod = False
            oldus = g.unicodes
            if not oldus:
                oldus = []
            if n in self.n2u:
                newus = self.n2u.get(n, [])
                if newus != oldus:
                    mod = True
            else:
                if not keepUnicodes:
                    if g.unicode:
                        newus = []
                        mod = True
            if mod:
                assignUnicodes(g, newus)
                print("%s: [%s] -> [%s]" % (
                    n, ' '.join(['%04X' % u for u in oldus]), ' '.join(['%04X' % u for u in g.unicodes])
                    ))
                if flagModified:
                    lg = fl6.flGlyph(g, f)
                    lg.mark = flagModified
                mods += 1
        return mods

class dlg_generateUnicode(QtGui.QDialog):

    def __init__(self):
        super(dlg_generateUnicode, self).__init__()
        self.n2u = {}
        # Insert your default folder for custom NAM files
        self.namFolder = r''
        # Set to True if you want to keep Unicodes for glyphs not in the NAM
        self.keepUnicodes = True
        # Enter color flag integer if you want to flag modified glyphs, or None
        self.flagModified = 1

        self.f = CurrentFont()
        self.fPath = self.f.path
        self.fFolder = os.path.dirname(self.fPath)
        self.fPathBase = os.path.splitext(os.path.basename(self.fPath))[0]
        self.fgnu = fontGlyphNameUnicodes(self.f)

        if not self.namFolder:
            if fl.userpath:
                self.namFolder = fl.userpath
            else:
                self.namFolder = self.fFolder

        # -- Flag color selector
        self.cmb_flag = QtGui.QComboBox()
        colorNames = QtGui.QColor.colorNames()

        for i in range(len(colorNames)):
            self.cmb_flag.addItem(colorNames[i])
            self.cmb_flag.setItemData(i, QtGui.QColor(colorNames[i]), QtCore.Qt.DecorationRole)

        self.cmb_flag.insertItem(0, 'None')
        self.cmb_flag.setCurrentIndex(0)

        # - Options
        self.chk_keepUnicodes = QtGui.QCheckBox('Keep Unicodes for glyphs not in NAM')
        self.chk_keepUnicodes.setCheckState(QtCore.Qt.Checked)

        # - Buttons
        self.btn_open = QtGui.QPushButton('&Open NAM file')
        self.btn_open.clicked.connect(self.openNamFile)
        self.btn_save = QtGui.QPushButton('&Save NAM file')
        self.btn_save.clicked.connect(self.saveNamFile)
        self.btn_run = QtGui.QPushButton('&Generate Unicodes')
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self.generateUnicodes)

        # - Build layouts
        layoutV = QtGui.QVBoxLayout()
        layoutV.addWidget(self.btn_open)
        layoutV.addWidget(QtGui.QLabel('Flag modified glyphs:'))
        layoutV.addWidget(self.cmb_flag)
        layoutV.addWidget(self.chk_keepUnicodes)
        layoutV.addWidget(self.btn_run)
        layoutV.addWidget(self.btn_save)

        # - Set Widget
        self.setLayout(layoutV)
        self.setWindowTitle('%s %s' %(app_name, __version__))
        self.setGeometry(300, 300, 220, 120)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # Always on top!!
        self.show()

    def getColorFlag(self):
        if self.cmb_flag.currentText != 'None':
            return QtGui.QColor(self.cmb_flag.currentText).hue()
        else:
            return None

    def openNamFile(self):
        namPath = QtGui.QFileDialog.getOpenFileName(
            None,
            "Choose NAM file",
            self.namFolder,
            "Unicode-to-glyphname NAM (*.nam)"
            )
        if namPath:
            self.fgnu.readFromNamPath(namPath)
            print('Opened %s with Unicode mappings for %s glyphs.\nClick "Generate Unicodes" to generate the Unicodes based on these mappings.' % (namPath, len(self.fgnu.n2u)))
            self.btn_run.setEnabled(True)

    def saveNamFile(self):
        namPathDefault = os.path.join(self.namFolder, self.fPathBase + '.nam')
        namPath = QtGui.QFileDialog.getSaveFileName(
            None,
            "Save current font Unicodes as NAM file",
            namPathDefault,
            "Unicode-to-glyphname NAM (*.nam)"
            )
        self.fgnu.writeToNamPath(namPath, self.f)
        print('Saved %s' % (namPath))
        self.accept()

    def generateUnicodes(self):
        mods = self.fgnu.writeToFont(
          self.f,
          keepUnicodes = self.chk_keepUnicodes.isChecked(),
          flagModified = self.getColorFlag()
          )
        updateFont(self.f)
        print('%s glyphs remapped.' % (mods))
        self.accept()

# - RUN ------------------------------
dialog = dlg_generateUnicode()