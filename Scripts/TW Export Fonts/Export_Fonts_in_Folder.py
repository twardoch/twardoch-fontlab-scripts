#FLM: Export Fonts in Folder
# Python script for FontLab 7
# By Adam Twardoch, 2020-04-02
# Licensed at your choice under:
# - CC-0 (public domain)
# - MIT license, Copyright (c) 2020 Adam Twardoch

from __future__ import print_function, unicode_literals
import os.path
import os
import re
import datetime
import fontlab as fl6
import fontgate as fgt
from PythonQt import QtCore, QtGui
from fontlab import *
from glob import glob
import tempfile
import shutil

__version__ = '0.2'
app_name = 'Export Fonts in Folder'

ws = flWorkspace.instance()
main = ws.mainWindow
itm = flItems
pref = flPreferences.instance()

def getQAct(name):
    for wgt in main.children():
        if wgt.objectName == name:
            return wgt

class ExportFontsInFolder(object):

    def __init__(self):
        self.fontTypes = ['*.vfc', '*.vfj', '*.vfb', '*.otf', '*.ttf', '*.glyphs']
        self.srcFolder = pref.exportSaveFolder
        if len(ws.packages()):
            p = flPackage(CurrentFont()).path
            if p:
                self.srcFolder = os.path.split(p)[0]
        self.prefDestFolder = pref.exportDestinationFolder
        self.destFolder = self.prefDestFolder
        self.tmp = tempfile.mktemp(prefix='com.fontlab.export.')
        self.srcPaths = []
        self.destFormat = None
        self.multiFormat = False
        self.qActExportFont = getQAct('actionExport_Font')
        self.qActExportFontAs = getQAct('actionExport_Fonts')

    def tmpMake(self):
        os.makedirs(self.tmp)
        if os.path.isdir(self.tmp):
            return self.tmp
        else:
            return None

    def tmpDel(self):
        return self.deletePath(self.tmp)

    def qActRun(self, qAct):
        if qAct.enabled:
            qAct.trigger()
        else:
            self.qActRun(qAct)

    def findFontsInFolder(self, inFolder = None):
        if not inFolder:
            inFolder = self.srcFolder
        if not inFolder:
            return
        fontTypes = self.fontTypes + [t.upper() for t in self.fontTypes]
        for ext in fontTypes:
            self.srcPaths.extend(glob(os.path.join(inFolder, ext)))
            self.srcPaths.extend(glob(os.path.join(inFolder, '**', ext)))

    def closeFont(self, pk = None, save = False):
        if not pk:
            pk = flPackage(CurrentFont())
        itm.notifyPackageClosed(pk)
        itm.notifyPackageRemoved(pk)
        pk.close(save)

    def closeAllFonts(self):
        for pko in ws.packages():
            pk = flPackage(pko)
            closeFont(pk)

    def openFont(self, path):
        return itm.requestLoadingFont(path)

    def deletePath(self, path):
        if not os.path.exists(path):
            return True
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except:
            print('--- [ERROR] Cannot remove:')
            print(path)
            return False

    def convertFont(self, path = None):
        if not path:
            return False
        if not self.destFormat:
            self.chooseFormat()
        relpath = path.replace(self.srcFolder, '')
        exportpath = self.destFolder.rstrip(os.path.sep) + os.path.sep + relpath.lstrip(os.path.sep)
        exportfolder, exportfileext = os.path.split(exportpath)
        if not os.path.isdir(exportfolder):
            self.deletePath(exportfolder)
            os.makedirs(exportfolder)
        exportbasename = os.path.splitext(exportfileext)[0]
        tmp = self.tmpMake()
        if not tmp:
            print('--- [ERROR] Cannot make temporary folder:')
            print(tmp)
            return False
        print('---')
        print('--- Opening:')
        print(path)
        self.openFont(path)
        pk = flPackage(CurrentFont())
        if pref.exportDestinationFolder == self.tmp:
            self.qActRun(self.qActExportFont)
        self.closeFont(pk)
        print(pref.exportDestinationFolder)
        exportedPaths = glob(os.path.join(self.tmp, '*.*'))
        if not len(exportedPaths) > 0:
            print('--- [ERROR] Cannot convert:')
            print(path)
            shutil.rmtree(self.tmp)
            return
        if len(exportedPaths) > 1:
            destpath = os.path.join(exportfolder, exportbasename)
            self.deletePath(destpath)
            print('--- Exporting to:')
            print(destpath)
            shutil.move(tmp, destpath)
        else:
            srcpath = exportedPaths[0]
            srcext = os.path.splitext(srcpath)[1]
            destpath = os.path.join(exportfolder, exportbasename + srcext)
            self.deletePath(destpath)
            print('--- Exporting to:')
            print(destpath)
            shutil.move(srcpath, destpath)
        self.tmpDel()

    def convertFonts(self):
        self.findFontsInFolder()
        if not os.path.isdir(self.destFolder):
            print('--- [ERROR] Cannot write to folder:')
            print (self.destFolder)
            return
        for path in self.srcPaths:
            self.convertFont(path)
        pref.exportDestinationFolder = self.prefDestFolder
        print('---')
        print('--- Finished exporting to:')
        print(self.destFolder)

    def chooseFormat(self):
        tmp = self.tmpMake()
        if not tmp:
            print('--- [ERROR] Cannot make temporary folder:')
            print(self.tmp)
            return False
        pref.exportConflictMode = 3
        pref.exportDestinationMode = 3
        pref.exportOrganizeMode = 0
        pref.exportDestinationFolder = self.tmp
        pk = flPackage()
        pk.addAxis(flAxis('weight', 'wght', 'wt'))
        pk.addMaster('Light', False, pk, None, False, False)
        pk.addMaster('Bold', False, pk, None, False, False)
        for m in pk.masters[1:]: pk.addInstance(flInstance(m, m, pk.location(m)))
        self.qActRun(self.qActExportFontAs)
        exportedPaths = glob(os.path.join(self.tmp, '*.*'))
        if len(exportedPaths) > 0:
            if len(exportedPaths) > 1:
                self.multiFormat = True
            self.destFormat = os.path.splitext(exportedPaths[0])[1]
        self.closeFont(pk)
        self.tmpDel()

class dlg_exportFontsInFolder(QtGui.QDialog):

    def __init__(self):
        super(dlg_exportFontsInFolder, self).__init__()
        self.export = ExportFontsInFolder()

        layoutV = QtGui.QVBoxLayout()

        # Source folder
        self.lay_src = QtGui.QHBoxLayout()
        self.lbl_src = QtGui.QLabel('Source folder:')
        self.lbl_src.setFixedWidth(120)
        self.lay_src.addWidget(self.lbl_src)
        self.edt_srcFolder = QtGui.QLineEdit()
        self.edt_srcFolder.setText(self.export.srcFolder)
        self.edt_srcFolder.setToolTip('Will recursively find source files in this folder')
        self.lay_src.addWidget(self.edt_srcFolder)
        self.btn_pickSrcFolder = QtGui.QPushButton('…')
        self.btn_pickSrcFolder.clicked.connect(self.pickSrcFolder)
        self.lay_src.addWidget(self.btn_pickSrcFolder)
        layoutV.addLayout(self.lay_src)

        # Source folder
        self.lay_types = QtGui.QHBoxLayout()
        self.lbl_types = QtGui.QLabel('File types:')
        self.lbl_types.setFixedWidth(120)
        self.lay_types.addWidget(self.lbl_types)
        self.edt_types = QtGui.QLineEdit()
        self.edt_types.setText(" ".join(self.export.fontTypes))
        self.edt_types.setToolTip('Space-separated filename patterns to find files in Source folder')
        self.lay_types.addWidget(self.edt_types)
        layoutV.addLayout(self.lay_types)

        # Destination folder
        self.lay_dest = QtGui.QHBoxLayout()
        self.lbl_dest = QtGui.QLabel('Destination folder:')
        self.lbl_dest.setFixedWidth(120)
        self.lay_dest.addWidget(self.lbl_dest)
        self.edt_destFolder = QtGui.QLineEdit()
        self.edt_destFolder.setText(self.export.destFolder)
        self.edt_destFolder.setToolTip('Will place exported fonts in this folder, recreating the Source folder structure')
        self.lay_dest.addWidget(self.edt_destFolder)
        self.btn_pickDestFolder = QtGui.QPushButton('…')
        self.btn_pickDestFolder.clicked.connect(self.pickDestFolder)
        self.lay_dest.addWidget(self.btn_pickDestFolder)
        layoutV.addLayout(self.lay_dest)

        # Run layout
        self.lay_run = QtGui.QHBoxLayout()
        self.lbl_format = QtGui.QLabel('Click <i>Export Fonts As</i>, choose <i>Content</i>, choose/customize <i>Profile</i>.<br /><b>Don’t</b> change <i>Destination</i> settings there. Click <i>Export</i>.')
        self.lbl_format.setStyleSheet('font-size:10pt;')
        self.lay_run.addWidget(self.lbl_format)
        self.lay_run.addStretch()
        self.btn_cancel = QtGui.QPushButton('Cancel')
        self.btn_cancel.clicked.connect(self.cancel)
        self.lay_run.addWidget(self.btn_cancel)
        self.btn_run = QtGui.QPushButton('&Export Fonts As')
        self.btn_run.setDefault(True)
        self.btn_run.setFocus()
        self.btn_run.clicked.connect(self.run)
        self.lay_run.addWidget(self.btn_run)
        layoutV.addLayout(self.lay_run)

        # - Set Widget
        self.setLayout(layoutV)
        self.setWindowTitle('%s %s' %(app_name, __version__))
        self.setGeometry(300, 300, 600, 200)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # Always on top!!
        self.show()

    def cancel(self):
        self.reject()

    def pickSrcFolder(self):
        self.edt_srcFolder.setText(QtGui.QFileDialog.getExistingDirectory(
            None, "Choose source folder", self.edt_srcFolder.text, QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks))

    def pickDestFolder(self):
        self.edt_destFolder.setText(QtGui.QFileDialog.getExistingDirectory(
            None, "Choose folder", self.edt_destFolder.text, QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks))

    def exportFonts(self):
        self.export.findFontsInFolder()
        if not os.path.isdir(self.export.destFolder):
            print('--- [ERROR] Cannot write to folder:')
            print (self.export.destFolder)
            return
        progressTotal = len(self.export.srcPaths)
        for pathi, path in enumerate(self.export.srcPaths):
            self.btn_run.setText('%d / %d' % (pathi+1, progressTotal))
            self.export.convertFont(path)
        pref.exportDestinationFolder = self.export.prefDestFolder
        print('---')
        print('--- %s fonts exported to:' % (progressTotal))
        print(self.export.destFolder)

    def run(self):
        self.export.srcFolder = self.edt_srcFolder.text.rstrip(os.path.sep)
        self.export.destFolder = self.edt_destFolder.text.rstrip(os.path.sep)
        self.export.fontTypes = self.edt_types.text.lstrip().rstrip().split(' ')
        self.export.chooseFormat()
        if self.export.destFormat:
            self.btn_run.setEnabled(False)
            self.exportFonts()
            self.accept()

# - RUN ------------------------------
dialog = dlg_exportFontsInFolder()