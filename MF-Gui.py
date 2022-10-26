# -*- coding: utf-8 -*-
"""
Created on Sat Apr 01 19:04:16 2017

@author: Riccardo Budai
"""
#!/usr/bin/env python
"""
server via Serial : pySerial
connect via usb cable to the microcontroller device
source of microcontroller firmware on /Home/Arduino/tests/encoderInterrupt
"""

import os
import time
from time import strftime
from collections import namedtuple
#
from S4_screenshot import Screenshot
from S4_settings import classSettings, sbjActualRec
from S4_Tables import dbaseH5Table
from S4_tugo import classPronoSupTest
from S4_review import classReview
#from S4_LSTM import serialLSTM
from S4_classifyMD import classMD
from S4_audio import classAudio
# - design widget
from mainWindow_ui import *

# - main class for window GUI ---------------------------------------

"""
   # .- parameters for logging file
    log_filename = "{}.log".format(app_title)
    log_max_bytes = 5120
    log_default_level = 1
    log_default_console_log = False
"""


class MainWindow(QtWidgets.QMainWindow):
    windowList = []

    def __init__(self, fileName = None):
        super(MainWindow, self).__init__()       
        self.ui = Ui_mainBtForm()
        self.ui.setupUi(self)

        self.move(0, 0)

        # - default palette colors
        self.paletteDef = QtGui.QPalette()
        #
        # self.textEdit = QtWidgets.QTextEdit()
        # self.setCentralWidget(self.textEdit)

        self.textEdit = self.ui.textEdit
        self.textEdit.append('MD->'+time.asctime(time.localtime(time.time())))
        # self.textEdit.setDocumentTitle('MF-fb > '+time.asctime(time.localtime(time.time())))
        # self.textEdit.setPlainText('MF-fb > '+time.asctime(time.localtime(time.time())))

        # - retrieve actual working path
        self.pathAct = os.getcwd()

        # - proposed data for deafault subject : anonimous or defined
        # - populate subject data
        # self.ui.lbl_dbase.setText(self.pathAct)
        # self.ui.lbl_name.setText('name')
        # self.ui.lbl_surname.setText('surname')
        # self.ui.lbl_nascita.setText('05/11/1953')
        # self.ui.lbl_sex.setText('M')
        # self.ui.lbl_dateSes.setText(QtCore.QDate.currentDate().toString())
        # self.ui.lbl_protSes.setText('MOV disorders monitor')
        #
        self.createActions()
        #self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        #
        self.setCurrentFile('')
        # - dbase and tables HDF5
        self.doTable = False
        self.recSBJ = 0
        self.recSBJPrev = 0
        # - load start thumbnail image
        root = QtCore.QFileInfo(__file__).absolutePath()
        #pixmap = QtGui.QPixmap(root+'/images/elbow3FLX_EXTthumb.jpg')
        pixmap = QtGui.QPixmap(root + '/images/IMG_S4-BTthumb.jpg')
        #print('thumb = ', pixmap.height(), pixmap.width())
        #self.ui.pixLabel.setPixmap(pixmap)
        #self.ui.pixLabel.show()

        # - menu ----------------------------------------------------
        menuBar = self.menuBar()
        #
        self.fileMenu = menuBar.addMenu('&File')
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        #
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAct)
        self.fileMenu.addAction(self.exitAct)
        #
        editMenu = menuBar.addMenu('&Edit')
        self.dbaseMenu = menuBar.addMenu('&Dbase')
        self.dbaseMenu.addAction(self.reviewData)
        self.dbaseMenu.addAction(self.sbjDataTable)
        #
        self.utilMenu = menuBar.addMenu('&Utility')
        #self.utilMenu.addAction(self.diagnosticaGen)
        #self.utilMenu.addAction(self.dateTimeAct)
        self.utilMenu.addAction(self.screenSHAct)
        #
        self.S4Menu = menuBar.addMenu('&MD')
        self.S4Menu.addAction(self.settingsRT)
        self.S4Menu.addAction(self.audioRT)
        #self.S4Menu.addAction(self.biofeedRT)
        #
        self.S4Menu.addAction(self.pronosupRT)
        #self.S4Menu.addAction(self.trainingRT)
        #self.S4Menu.addAction(self.trainingRTHD)
        #self.S4Menu.addAction(self.demoData)
        #
        self.helpMenu = menuBar.addMenu('Help')
        self.helpMenu.addAction(self.helpInfo)
        #
        # self.controlSettings = classSettings()

        # - apertura file database HDF5
        """
        # - sets default data of new subiject
        self.newSbj = sbjActualRec()
        self.newSbj.sbjID = 0
        self.newSbj.name = 'name'
        self.newSbj.surname = 'surname'
        self.newSbj.sex = 'M'
        self.newSbj.heigth = 170
        self.newSbj.weigth = 72
        self.newSbj.day = 5
        self.newSbj.month = 12
        self.newSbj.year = 1980
        self.newSbj.scolar = 0
        self.newSbj.patRsp = 0
        self.newSbj.patEcg = 0
        self.newSbj.address = 'via '
        self.newSbj.phone = '1234'
        self.newSbj.notes = 'notes:'
        """
        # - open database panel with list of subjects
        self.dataSBJ()

        # - date time
        self.displayDate()
        self.displayTime()

        # - timer to update display time now: 1 minuto
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(60000)   # - minutes
        self.timer.timeout.connect(self.displayTime)
        self.timer.start()

        root = QtCore.QFileInfo(__file__).absolutePath()
        pixmap = QtGui.QPixmap(root+'/images/IMG_IMU291x235.jpg')
        self.ui.labelMain.setPixmap(pixmap)
        # -  launch settings
        #self.settingsOperaz()

    def createActions(self):
        # - azioni collegate alle singole voci di menu
        root = QtCore.QFileInfo(__file__).absolutePath()
        self.newAct = QtWidgets.QAction(QtGui.QIcon(root+'/images/new.png'), "&New", self, shortcut=QtGui.QKeySequence.New,
                        statusTip="Create a new file", triggered=self.newFile)

        self.openAct = QtWidgets.QAction(QtGui.QIcon(root+'/images/open.png'), "&Open...", self, shortcut=QtGui.QKeySequence.Open,
                        statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QtWidgets.QAction(QtGui.QIcon(root+'/images/save.png'), "&Save", self, shortcut=QtGui.QKeySequence.Save,
                        statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QtWidgets.QAction("Save &As...", self, shortcut=QtGui.QKeySequence.SaveAs,
                        statusTip="Save the document under a new name", triggered=self.saveAs)
        
        self.cutAct = QtWidgets.QAction(QtGui.QIcon(root + '/images/cut.png'), "Cu&t", self,
                shortcut = QtGui.QKeySequence.Cut,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.textEdit.cut)

        self.copyAct = QtWidgets.QAction(QtGui.QIcon(root + '/images/copy.png'), "&Copy", self,
                shortcut=QtGui.QKeySequence.Copy,
                statusTip="Copy the current selection's contents to the clipboard",
                triggered=self.textEdit.copy)

        self.pasteAct = QtWidgets.QAction(QtGui.QIcon(root + '/images/paste.png'), "&Paste",
                self, shortcut=QtGui.QKeySequence.Paste,
                statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.textEdit.paste)

        # - classifydata recorded
        self.lstmData = QtWidgets.QAction(QtGui.QIcon(root + '/images/dbase.png'), "Review recorded sessions", self, statusTip ="classify recorded sessions",
                        triggered=self.classifyData)

        # - review and analize data recorded 
        self.reviewData = QtWidgets.QAction(QtGui.QIcon(root + '/images/dbase.png'), "Review recorded sessions", self, statusTip ="review of previously recorded sessions",
                        triggered=self.recordedData)
        self.sbjDataTable = QtWidgets.QAction("subject info DB", self, statusTip="subject data info in Table",
                        triggered=self.dataSBJ)
        
        # - display real time data, settings for real time functions, biofeedback
        self.settingsRT = QtWidgets.QAction(QtGui.QIcon(root + '/images/settings.png'), "settings", self, statusTip="retrieve and edit settings for tests",
                        triggered=self.settingsOperaz)

        self.pronosupRT = QtWidgets.QAction(QtGui.QIcon(root + '/images/biofeedRSP.png'), "acquire IMU movements", self, statusTip = "acquisition of IMU accelerations & angular velocities",
                        triggered=self.pronosupinationRT)

        self.screenSHAct = QtWidgets.QAction("Screen Shot", self, statusTip="Take a screen shot of the display with saving function",
                        triggered=self.getScreenShot)

        self.audioRT = QtWidgets.QAction(QtGui.QIcon(root + '/images/biofeedRSP.png'), "acquire AUDIO from mic", self, statusTip = "acquisition of AUDIO from microphone",
                                         triggered=self.audioRecord)
        #
        self.closeAct = QtWidgets.QAction("&Close", self, shortcut="Ctrl+W", statusTip="Close this window", triggered=self.close)

        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit the application", triggered=QtWidgets.qApp.closeAllWindows)

        self.helpInfo = QtWidgets.QAction("About &MD", self, statusTip="Show the MD documentation file", triggered= self.about)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)
        
        self.S4_FuToolBar = self.addToolBar("MD")
        self.S4_FuToolBar.addAction(self.settingsRT)
        self.S4_FuToolBar.addAction(self.lstmData)
        #self.S4_FuToolBar.addAction(self.biofeedRT)
        self.S4_FuToolBar.addAction(self.pronosupRT)
        self.S4_FuToolBar.addAction(self.audioRT)
        #self.S4_FuToolBar.addAction(self.trainingRTHD)
        #self.S4_FuToolBar.addAction(self.trainingADVRT)
        #
        self.S4_FuToolBar.addAction(self.reviewData)

    def createStatusBar(self):
        # - barra di stato bottom
        self.statusBar().showMessage("MD ready to go...")
    
# - MD specific operative functions ***************************************
# ****************************************************************************
    #
    def settingsOperaz(self):
        print('global and specific settings for realtime procedures')
        self.textEdit.append('MD > '+'settings: global & detailed')
        # -
        otherS = classSettings()
        # - from settings data on actual sbject to set test to perform
        otherS.newSbjRec.connect(self.dataSBJ)
        # - show settings
        MainWindow.windowList.append(otherS)
        otherS.move(self.x()+self.width()+70, 0)
        otherS.show()

    def audioRecord(self):
        # - activate system audio recorder from microphone
        # - visualize bar of signal strength
        # - recording on file in .wav format
        self.textEdit.append('MD > ' + 'show / rec audio')
        otherAu = classAudio()
        MainWindow.windowList.append(otherAu)
        otherAu.move(self.x()+self.width()+5, self.y())
        otherAu.show()

    def pronosupinationRT(self):
        self.textEdit.append('MD > '+'acquisition of IMU devices')
        # - object .recSbj
        otherPS = classPronoSupTest(self.recSbj)
        MainWindow.windowList.append(otherPS)
        otherPS.move(self.x()+self.width()+5, self.y())
        otherPS.show()

    def classifyData(self):
        # - open framework to deal with classifications
        self.textEdit.append('MD > ' + 'classifications')
        otherClassMD = classMD()
        MainWindow.windowList.append(otherClassMD)
        otherClassMD.move(self.x()+self.width()+5, self.y())
        otherClassMD.show()

    def recordedData(self):
        # - review data recorded on files or DBase
        print('Review of recorded data from DBase')
        self.textEdit.append('MD > '+'review of recorded data')
        # - todo load class to review data recorded
        classReview()
        """
        #otherR = classReview() #self.dbTable.recAct, self.dbTable.dosesAct)
        MainWindow.windowList.append(otherR)
        otherR.move(self.x()+self.width()//2, self.y()+25)
        otherR.show()
        """

    def dataSBJ(self):
        # - update main window panel with data of recording subject
        # self.recSbj = self.newSbj
        # self.ui.lbl_name.setText(self.recSbj.name)
        # self.ui.lbl_surname.setText(self.recSbj.surname)
        # self.ui.lbl_sex.setText(self.recSbj.sex)
        # - data di nascita formttata in unica stringa gg/mm/aaaa
        # self.ui.lbl_nascita.setText(str(self.recSbj.day)+'/'+str(self.recSbj.month)
        #                            +'/'+str(self.recSbj.year))

        # - controllo dati soggetto in pyTables : search / append / modify
        # print('Recording subject.....QTREE....')
        self.textEdit.append('MD > '+'data subject in Tables')
        """
        # - todo populate treeWidget with subject data from DBTable
        p1 = QTreeWidgetItem()
        # - column = 0
        self.ui.treeWidget.itemWidget(p1, 0)
        p1.setText(0, "02")
        # - column = 1
        p11 = QTreeWidgetItem()
        self.ui.treeWidget.itemWidget(p11, 1)
        p1.setText(1, "rosmary")
        # - column = 2
        p12 = QTreeWidgetItem()
        self.ui.treeWidget.itemWidget(p12, 2)
        p1.setText(2, "blanco")
        # - column = 3
        p13 = QTreeWidgetItem()
        self.ui.treeWidget.itemWidget(p13, 3)
        p1.setText(3, "22/04/1980")
        # - add child items
        for i in range(5):
            p1_child = QTreeWidgetItem()
            self.ui.treeWidget.itemWidget(p1_child, 1)
            p1_child.setText(1, "file rec:" + str(i))
            p11.addChild(p1_child)

        # - set header labels
        # p2 = self.ui.treeWidget.itemWidget(["01", "riccardo", "budai", "05/11/1953"])
        self.ui.treeWidget.setHeaderLabels(["id", "name", "surname", "birdth"])
        # self.ui.treeWidget.addTopLevelItem(p2)
        self.ui.treeWidget.addTopLevelItem(p1)
        """
        
        # - create and show dbase table obj
        self.dbTable = dbaseH5Table(0, self.x(), self.height()+10)
        # m = MyStruct(field1="foo", field2="bar", field3="baz")

        sbjActualRec = namedtuple("sbjActualRec", "name surname sex day month year")
        print(sbjActualRec)

# -----------------------------------------------------------------------------
    def newFile(self):
        if self.maybeSave():
            self.textEdit.clear()
            self.setCurrentFile('')

    def open(self):
        if self.maybeSave():
            fileName, _ = QtGui.QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)
        #
        return self.saveAs()

    def saveAs(self):
        fileName, _ = QtGui.QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)
        #
        return False
    
    def maybeSave(self):
        if self.textEdit.document().isModified():
            ret = QtWidgets.QMessageBox.warning(self, "MD",
                    "The document has been modified.\nDo you want to save "
                    "your changes?",
                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)

            if ret == QtWidgets.QMessageBox.Save:
                return self.save()

            if ret == QtWidgets.QMessageBox.Cancel:
                return False

        return True

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self, "Application",
                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return

        inf = QtCore.QTextStream(file)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.textEdit.setPlainText(inf.readAll())
        QtWidgets.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self, "Application",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QtCore.QTextStream(file)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outf << self.textEdit.toPlainText()
        QtWidgets.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName);
        self.statusBar().showMessage("File saved", 2000)
        return True          
    
    def about(self):
        QtGui.QMessageBox.about(self, "About MD-tracking",
                "The <b>MD</b> enable monitoring and analisys of signals from IMU, "
                "detecting (<b>antero / posterior</b>) and (<b>Latero / Lateral</b>) inclinations. "
                "Prototyping Laboratory Italy <b>VBLab - 2018</b>")

    def readSettings(self):
        settings = QtCore.QSettings("Trolltech", "Application Example")
        pos = settings.value("pos", QtCore.QPoint(0, 0))
        size = settings.value("size", QtCore.QSize(400, 200))
        #self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QtCore.QSettings("Trolltech", "Application Example")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        
    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.textEdit.document().setModified(False)
        self.setWindowModified(False)
        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'
        #self.setWindowTitle("%s[*] - Application" % shownName)

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

    """
    def setDiagnostica(self):
        # - window for diagnostica and comunicatio to Bluetooth
        other = diagnostic_class()
        MainWindow.windowList.append(other)
        other.move(self.x() + self.width(), self.y())
        other.show()
    """
    """
    def getDateTime(self):
        # - window for the date time
        other = ipv4_time()
        MainWindow.windowList.append(other)
        other.move(self.x() + self.width(), self.y())
        other.show()
    """

    def getScreenShot(self):
        # - window for the screenshot function
        other = Screenshot()
        MainWindow.windowList.append(other)        
        other.move(self.x() + self.width(), self.y())
        other.show() 

    def displayDate(self):
        self.paletteDef.setColor(QtGui.QPalette.Foreground, QtCore.Qt.blue)
        self.ui.labelDate.setPalette(self.paletteDef)
        self.ui.labelDate.setText(QtCore.QDate.currentDate().toString())

    def displayTime(self):
        # - visualizza ora corrente ogni minuto su timer callback
        self.ui.lcdTime.display(strftime("%H"+":"+"%M"))  # +":"+"%S"))
        if self.doTable:
            # - verifica i dati del record sbj che non sia variato
            self.recSBJ = self.dbTable.dorecAct()
            if self.recSBJ != self.recSBJPrev:
                self.recPanelUpdate(self.recSBJ)
                self.recSBJPrev = self.recSBJ

    def recPanelUpdate(self, numRec):
        # - ottiene idati del record sbj dalla tabella HDF5
        self.recordSBJ = self.dbTable.dorecordActual(self.recSBJ)
        self.ui.lbl_name.setText(''.join(chr(c) for c in self.recordSBJ['Name']))
        self.ui.lbl_surname.setText(''.join(chr(c) for c in self.recordSBJ['surName']))
        self.ui.lbl_nascita.setText(str(self.recordSBJ['sbjNascD'])+" / "
                                               +str(self.recordSBJ['sbjNascM'])+" / "
                                                +str(self.recordSBJ['sbjNascY']))
        self.ui.lbl_sex.setText(''.join(chr(c) for c in self.recordSBJ['sbjSex']))
        self.ui.lbl_dateSes.setText(''.join(chr(c) for c in self.recordSBJ['sesDate']))
        self.ui.lbl_protSes.setText(''.join(chr(c) for c in self.recordSBJ['sesProtocol']))

# ===========================================================================================
# app = None

def main():
    import sys
    print(sys.platform)
    appmd = QtWidgets.QApplication([])
    mainwin = MainWindow()
    mainwin.show()
    appmd.exec_()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
