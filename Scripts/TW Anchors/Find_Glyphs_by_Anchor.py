#FLM: Find Glyphs by Anchor
# Python script for FontLab 7
# By Adam Twardoch, 2020-05-20
# Licensed at your choice under:
# - CC-0 (public domain)
# - MIT license, Copyright (c) 2020 Adam Twardoch

from __future__ import print_function

from PythonQt import QtGui
from typerig.proxy import pFont, pGlyph
from fontlab import *

app_version = '0.01'
app_name = 'Find Glyphs by Anchor'
ws = flWorkspace.instance()

def findAllAnchors(font):
    anchorNames = []
    for glyph in font.pGlyphs():
        current_masters = glyph.masters()
        if len(current_masters):
            for layer in current_masters:
                for anchor in layer.anchors:
                    anchorNames.append(anchor.name)
    anchorNames = sorted(list(set(anchorNames)))
    return anchorNames

def findGlyphsWithAnchor(findAnchorName, font, allMasters = True):
    foundGlyphs = []
    for glyph in font.pGlyphs():
        anchorNames = []
        if allMasters:
            current_masters = glyph.masters()
            if len(current_masters):
                for layer in current_masters:
                    for anchor in layer.anchors:
                        anchorNames.append(anchor.name)
        else:
            for anchor in glyph.anchors(None):
                anchorNames.append(anchor.name)
        if findAnchorName in anchorNames:
            foundGlyphs.append(glyph.name)
    return foundGlyphs

class AComboBox(QtGui.QComboBox):
    # - Custom QLine Edit extending the contextual menu with anchor names
    def __init__(self, anchors = [], *args, **kwargs):
        super(AComboBox, self).__init__(*args, **kwargs)
        self.setEditable(True)
        for anchorName in [''] + anchors:
            self.addItem(anchorName)

class dlg_selectGlyphsWithAnchor(QtGui.QDialog):
    def __init__(self):
        super(dlg_selectGlyphsWithAnchor, self).__init__()
        self.f = pFont()
        self.edt_anchorName = AComboBox(findAllAnchors(self.f))
        self.chk_allMasters = QtGui.QCheckBox('Search in all masters')
        self.chk_allMasters.setChecked(True)
        self.btn_select = QtGui.QPushButton('&Select')
        self.btn_select.setStatusTip('Select glyphs that have the anchor')
        self.btn_select.clicked.connect(self.selectGlyphsWithAnchor)

        layoutV = QtGui.QVBoxLayout()
        layoutV.addWidget(self.edt_anchorName)
        layoutV.addWidget(self.chk_allMasters)
        layoutV.addWidget(self.btn_select)

        self.setLayout(layoutV)
        self.setWindowTitle('%s %s' % (app_name, app_version))
        self.setGeometry(300, 300, 300, 120)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def selectGlyphsWithAnchor(self):
        selection = findGlyphsWithAnchor(self.edt_anchorName.currentText, self.f, allMasters = self.chk_allMasters.isChecked())
        if len(selection):
            self.f.unselectAll()
            print("/%s" % "/".join(selection))
            self.f.selectGlyphs(selection)
        self.accept()

dialog = dlg_selectGlyphsWithAnchor()
