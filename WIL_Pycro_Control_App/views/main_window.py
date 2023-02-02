from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(511, 263)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.spim_galvo_button = QtWidgets.QPushButton(self.centralwidget)
        self.spim_galvo_button.setGeometry(QtCore.QRect(110, 100, 101, 31))
        self.spim_galvo_button.setObjectName("spim_galvo_button")
        self.lsfm_label = QtWidgets.QLabel(self.centralwidget)
        self.lsfm_label.setGeometry(QtCore.QRect(30, 0, 451, 61))
        self.lsfm_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lsfm_label.setObjectName("lsfm_label")
        self.cls_button = QtWidgets.QPushButton(self.centralwidget)
        self.cls_button.setGeometry(QtCore.QRect(280, 100, 111, 31))
        self.cls_button.setObjectName("cls_button")
        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(200, 180, 111, 31))
        self.exit_button.setObjectName("exit_button")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 511, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Main Window"))
        self.spim_galvo_button.setText(_translate("MainWindow", "SPIM Galvo Setup"))
        self.lsfm_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:18pt;\">Klamath LSFM Control Software</span></p></body></html>"))
        self.cls_button.setText(_translate("MainWindow", "CLS Setup"))
        self.exit_button.setText(_translate("MainWindow", "Exit"))
