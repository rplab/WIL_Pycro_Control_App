from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AcquisitionDialog(object):
    def setupUi(self, AcquisitionDialog):
        AcquisitionDialog.setObjectName("AcquisitionDialog")
        AcquisitionDialog.resize(420, 176)
        self.fish_label = QtWidgets.QLabel(AcquisitionDialog)
        self.fish_label.setGeometry(QtCore.QRect(186, 30, 61, 20))
        self.fish_label.setAlignment(QtCore.Qt.AlignCenter)
        self.fish_label.setObjectName("fish_label")
        self.region_label = QtWidgets.QLabel(AcquisitionDialog)
        self.region_label.setGeometry(QtCore.QRect(180, 50, 71, 20))
        self.region_label.setAlignment(QtCore.Qt.AlignCenter)
        self.region_label.setObjectName("region_label")
        self.acquisition_label = QtWidgets.QLabel(AcquisitionDialog)
        self.acquisition_label.setGeometry(QtCore.QRect(0, 60, 421, 71))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.acquisition_label.setFont(font)
        self.acquisition_label.setAlignment(QtCore.Qt.AlignCenter)
        self.acquisition_label.setObjectName("acquisition_label")
        self.abort_button = QtWidgets.QPushButton(AcquisitionDialog)
        self.abort_button.setGeometry(QtCore.QRect(180, 140, 75, 23))
        self.abort_button.setObjectName("abort_button")
        self.time_point_label = QtWidgets.QLabel(AcquisitionDialog)
        self.time_point_label.setGeometry(QtCore.QRect(170, 10, 91, 16))
        self.time_point_label.setAlignment(QtCore.Qt.AlignCenter)
        self.time_point_label.setObjectName("time_point_label")

        self.retranslateUi(AcquisitionDialog)
        QtCore.QMetaObject.connectSlotsByName(AcquisitionDialog)

    def retranslateUi(self, AcquisitionDialog):
        _translate = QtCore.QCoreApplication.translate
        AcquisitionDialog.setWindowTitle(_translate("AcquisitionDialog", "Acquisition"))
        self.fish_label.setText(_translate("AcquisitionDialog", "Fish 1"))
        self.region_label.setText(_translate("AcquisitionDialog", "Region 1"))
        self.acquisition_label.setText(_translate("AcquisitionDialog", "No Acquisition Running"))
        self.abort_button.setWhatsThis(_translate("AcquisitionDialog", "<html><head/><body><p>Opens up Abort Dialog to abort running acquisition</p></body></html>"))
        self.abort_button.setText(_translate("AcquisitionDialog", "Abort"))
        self.time_point_label.setText(_translate("AcquisitionDialog", "Time point 1"))
