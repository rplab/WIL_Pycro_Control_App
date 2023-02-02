from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AcquisitionOrderDialog(object):
    def setupUi(self, AcquisitionOrderDialog):
        AcquisitionOrderDialog.setObjectName("AcquisitionOrderDialog")
        AcquisitionOrderDialog.resize(352, 215)
        AcquisitionOrderDialog.setInputMethodHints(QtCore.Qt.ImhNone)
        self.yes_button = QtWidgets.QPushButton(AcquisitionOrderDialog)
        self.yes_button.setGeometry(QtCore.QRect(90, 180, 75, 23))
        self.yes_button.setObjectName("yes_button")
        self.cancel_button = QtWidgets.QPushButton(AcquisitionOrderDialog)
        self.cancel_button.setGeometry(QtCore.QRect(190, 180, 75, 23))
        self.cancel_button.setObjectName("cancel_button")
        self.order_text_browser = QtWidgets.QTextBrowser(AcquisitionOrderDialog)
        self.order_text_browser.setGeometry(QtCore.QRect(50, 10, 251, 161))
        self.order_text_browser.setObjectName("order_text_browser")

        self.retranslateUi(AcquisitionOrderDialog)
        QtCore.QMetaObject.connectSlotsByName(AcquisitionOrderDialog)

    def retranslateUi(self, AcquisitionOrderDialog):
        _translate = QtCore.QCoreApplication.translate
        AcquisitionOrderDialog.setWindowTitle(_translate("AcquisitionOrderDialog", "Acquisition Order"))
        self.yes_button.setText(_translate("AcquisitionOrderDialog", "Yes"))
        self.cancel_button.setText(_translate("AcquisitionOrderDialog", "Cancel"))
        self.order_text_browser.setHtml(_translate("AcquisitionOrderDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Are you sure you want to do this? Setting this to SAMP_TIME will do the following:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">If set to SAMP_TIME, the outermost loop will be the fish number loop. The first fish will be imaged, then the program will wait for the next time point, then the same fish will be imaged, and so on. Only once all time points are complete will the program move on to the next fish, for which it will complete another full time series.</span></p></body></html>"))
