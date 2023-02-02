from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AbortDialog(object):
    def setupUi(self, AbortDialog):
        AbortDialog.setObjectName("AbortDialog")
        AbortDialog.resize(362, 112)
        self.abort_label = QtWidgets.QLabel(AbortDialog)
        self.abort_label.setGeometry(QtCore.QRect(70, 20, 201, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.abort_label.setFont(font)
        self.abort_label.setAlignment(QtCore.Qt.AlignCenter)
        self.abort_label.setObjectName("abort_label")
        self.abort_button = QtWidgets.QPushButton(AbortDialog)
        self.abort_button.setGeometry(QtCore.QRect(190, 70, 75, 23))
        self.abort_button.setObjectName("abort_button")
        self.cancel_button = QtWidgets.QPushButton(AbortDialog)
        self.cancel_button.setGeometry(QtCore.QRect(80, 70, 75, 23))
        self.cancel_button.setObjectName("cancel_button")

        self.retranslateUi(AbortDialog)
        QtCore.QMetaObject.connectSlotsByName(AbortDialog)

    def retranslateUi(self, AbortDialog):
        _translate = QtCore.QCoreApplication.translate
        AbortDialog.setWindowTitle(_translate("AbortDialog", "Abort"))
        self.abort_label.setText(_translate("AbortDialog", "Abort Acquisition?"))
        self.abort_button.setText(_translate("AbortDialog", "Abort"))
        self.cancel_button.setText(_translate("AbortDialog", "Cancel"))
