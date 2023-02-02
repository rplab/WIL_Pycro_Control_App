from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AcquisitionSettingsDialog(object):
    def setupUi(self, AcquisitionSettingsDialog):
        AcquisitionSettingsDialog.setObjectName("AcquisitionSettingsDialog")
        AcquisitionSettingsDialog.resize(426, 469)
        self.time_points_check_box = QtWidgets.QCheckBox(AcquisitionSettingsDialog)
        self.time_points_check_box.setGeometry(QtCore.QRect(60, 80, 81, 17))
        self.time_points_check_box.setObjectName("time_points_check_box")
        self.num_time_points_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.num_time_points_line_edit.setGeometry(QtCore.QRect(80, 110, 61, 20))
        self.num_time_points_line_edit.setObjectName("num_time_points_line_edit")
        self.time_points_interval_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.time_points_interval_line_edit.setGeometry(QtCore.QRect(80, 140, 61, 20))
        self.time_points_interval_line_edit.setObjectName("time_points_interval_line_edit")
        self.channel_order_move_up_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.channel_order_move_up_button.setGeometry(QtCore.QRect(210, 150, 75, 23))
        self.channel_order_move_up_button.setObjectName("channel_order_move_up_button")
        self.channel_order_move_down_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.channel_order_move_down_button.setGeometry(QtCore.QRect(210, 190, 75, 23))
        self.channel_order_move_down_button.setObjectName("channel_order_move_down_button")
        self.channel_order_list_view = QtWidgets.QListView(AcquisitionSettingsDialog)
        self.channel_order_list_view.setGeometry(QtCore.QRect(290, 130, 101, 101))
        self.channel_order_list_view.setObjectName("channel_order_list_view")
        self.channel_order_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.channel_order_label.setGeometry(QtCore.QRect(250, 80, 101, 20))
        self.channel_order_label.setAlignment(QtCore.Qt.AlignCenter)
        self.channel_order_label.setObjectName("channel_order_label")
        self.count_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.count_label.setGeometry(QtCore.QRect(40, 110, 31, 16))
        self.count_label.setObjectName("count_label")
        self.interval_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.interval_label.setGeometry(QtCore.QRect(30, 140, 51, 16))
        self.interval_label.setObjectName("interval_label")
        self.browse_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.browse_button.setGeometry(QtCore.QRect(60, 320, 75, 23))
        self.browse_button.setObjectName("browse_button")
        self.save_path_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.save_path_line_edit.setGeometry(QtCore.QRect(90, 350, 81, 20))
        self.save_path_line_edit.setObjectName("save_path_line_edit")
        self.save_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.save_label.setGeometry(QtCore.QRect(10, 350, 71, 20))
        self.save_label.setObjectName("save_label")
        self.start_acquisition_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.start_acquisition_button.setGeometry(QtCore.QRect(40, 410, 111, 23))
        self.start_acquisition_button.setObjectName("start_acquisition_button")
        self.total_images_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.total_images_label.setGeometry(QtCore.QRect(30, 200, 71, 16))
        self.total_images_label.setObjectName("total_images_label")
        self.total_images_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.total_images_line_edit.setGeometry(QtCore.QRect(110, 200, 61, 20))
        self.total_images_line_edit.setObjectName("total_images_line_edit")
        self.memory_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.memory_label.setGeometry(QtCore.QRect(30, 230, 71, 16))
        self.memory_label.setObjectName("memory_label")
        self.memory_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.memory_line_edit.setGeometry(QtCore.QRect(110, 230, 61, 20))
        self.memory_line_edit.setObjectName("memory_line_edit")
        self.num_images_per_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.num_images_per_label.setGeometry(QtCore.QRect(10, 170, 91, 20))
        self.num_images_per_label.setObjectName("num_images_per_label")
        self.num_images_per_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.num_images_per_line_edit.setGeometry(QtCore.QRect(110, 170, 61, 20))
        self.num_images_per_line_edit.setObjectName("num_images_per_line_edit")
        self.line_2 = QtWidgets.QFrame(AcquisitionSettingsDialog)
        self.line_2.setGeometry(QtCore.QRect(190, 60, 20, 491))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setLineWidth(4)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setObjectName("line_2")
        self.acquisition_settings_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.acquisition_settings_label.setGeometry(QtCore.QRect(80, 20, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.acquisition_settings_label.setFont(font)
        self.acquisition_settings_label.setAlignment(QtCore.Qt.AlignCenter)
        self.acquisition_settings_label.setObjectName("acquisition_settings_label")
        self.line_4 = QtWidgets.QFrame(AcquisitionSettingsDialog)
        self.line_4.setGeometry(QtCore.QRect(-60, 50, 531, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.line_4.setFont(font)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_4.setLineWidth(4)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setObjectName("line_4")
        self.memory_unit_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.memory_unit_label.setGeometry(QtCore.QRect(170, 230, 21, 16))
        self.memory_unit_label.setAlignment(QtCore.Qt.AlignCenter)
        self.memory_unit_label.setObjectName("memory_unit_label")
        self.researcher_line_edit = QtWidgets.QLineEdit(AcquisitionSettingsDialog)
        self.researcher_line_edit.setGeometry(QtCore.QRect(90, 380, 81, 20))
        self.researcher_line_edit.setObjectName("researcher_line_edit")
        self.researcher_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.researcher_label.setGeometry(QtCore.QRect(20, 380, 61, 20))
        self.researcher_label.setObjectName("researcher_label")
        self.save_acquisition_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.save_acquisition_label.setGeometry(QtCore.QRect(20, 290, 141, 20))
        self.save_acquisition_label.setAlignment(QtCore.Qt.AlignCenter)
        self.save_acquisition_label.setObjectName("save_acquisition_label")
        self.interval_label_2 = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.interval_label_2.setGeometry(QtCore.QRect(150, 140, 31, 16))
        self.interval_label_2.setObjectName("interval_label_2")
        self.show_acquisition_dialog_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.show_acquisition_dialog_button.setGeometry(QtCore.QRect(30, 440, 131, 23))
        self.show_acquisition_dialog_button.setObjectName("show_acquisition_dialog_button")
        self.line_3 = QtWidgets.QFrame(AcquisitionSettingsDialog)
        self.line_3.setGeometry(QtCore.QRect(-40, 270, 461, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.line_3.setFont(font)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setLineWidth(4)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.adv_settings_button = QtWidgets.QPushButton(AcquisitionSettingsDialog)
        self.adv_settings_button.setGeometry(QtCore.QRect(230, 350, 171, 23))
        self.adv_settings_button.setObjectName("adv_settings_button")
        self.adv_settings_label = QtWidgets.QLabel(AcquisitionSettingsDialog)
        self.adv_settings_label.setGeometry(QtCore.QRect(260, 290, 101, 20))
        self.adv_settings_label.setAlignment(QtCore.Qt.AlignCenter)
        self.adv_settings_label.setObjectName("adv_settings_label")

        self.retranslateUi(AcquisitionSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(AcquisitionSettingsDialog)

    def retranslateUi(self, AcquisitionSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        AcquisitionSettingsDialog.setWindowTitle(_translate("AcquisitionSettingsDialog", "Acquisition Settings"))
        self.time_points_check_box.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Enables time points (time series). If unchecked, acquistion script will only be performed once. If checked, the acquisition script will be repeated Count number of times with an interval of Interval minutes between them.</p></body></html>"))
        self.time_points_check_box.setText(_translate("AcquisitionSettingsDialog", "Time points"))
        self.num_time_points_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Number of time points in time series</p></body></html>"))
        self.time_points_interval_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Interval between time points in minutes</p></body></html>"))
        self.channel_order_move_up_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Moves channel up in channel order list</p></body></html>"))
        self.channel_order_move_up_button.setText(_translate("AcquisitionSettingsDialog", "Move Up"))
        self.channel_order_move_down_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Moves channel down in channel order list</p></body></html>"))
        self.channel_order_move_down_button.setText(_translate("AcquisitionSettingsDialog", "Move Down"))
        self.channel_order_list_view.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Order of channels in Z-stack, Snap, and Video acquisitions from top to bottom</p></body></html>"))
        self.channel_order_label.setText(_translate("AcquisitionSettingsDialog", "Channel Order"))
        self.count_label.setText(_translate("AcquisitionSettingsDialog", "Count:"))
        self.interval_label.setText(_translate("AcquisitionSettingsDialog", "Interval:"))
        self.browse_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Browse and choose directory for acquisition to be saved</p></body></html>"))
        self.browse_button.setText(_translate("AcquisitionSettingsDialog", "Browse..."))
        self.save_path_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Save location of acquisition</p></body></html>"))
        self.save_label.setText(_translate("AcquisitionSettingsDialog", "Save Location:"))
        self.start_acquisition_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Starts acquisition from settings set here and the region setup dialog. Also brings up the Acquisition Dialog which will provide updates during the acquisition and has an option to abort the acquisition.</p></body></html>"))
        self.start_acquisition_button.setText(_translate("AcquisitionSettingsDialog", "Start Acquisition"))
        self.total_images_label.setText(_translate("AcquisitionSettingsDialog", "Total Images:"))
        self.total_images_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Total number of images taken during the entire acquisition</p></body></html>"))
        self.memory_label.setText(_translate("AcquisitionSettingsDialog", "Total Memory:"))
        self.memory_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Total amount of data taken during the entire acquisition</p></body></html>"))
        self.num_images_per_label.setText(_translate("AcquisitionSettingsDialog", "Images per point:"))
        self.num_images_per_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Number of images  per time point</p></body></html>"))
        self.acquisition_settings_label.setText(_translate("AcquisitionSettingsDialog", "Acquisition Settings"))
        self.memory_unit_label.setText(_translate("AcquisitionSettingsDialog", "Gb"))
        self.researcher_line_edit.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Name of researcher</p></body></html>"))
        self.researcher_label.setText(_translate("AcquisitionSettingsDialog", "Researcher:"))
        self.save_acquisition_label.setText(_translate("AcquisitionSettingsDialog", "Save/Acquisition Start"))
        self.interval_label_2.setText(_translate("AcquisitionSettingsDialog", "min"))
        self.show_acquisition_dialog_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Starts acquisition from settings set here and the region setup dialog. Also brings up the Acquisition Dialog which will provide updates during the acquisition and has an option to abort the acquisition.</p></body></html>"))
        self.show_acquisition_dialog_button.setText(_translate("AcquisitionSettingsDialog", "Show Acquisition Dialog"))
        self.adv_settings_button.setWhatsThis(_translate("AcquisitionSettingsDialog", "<html><head/><body><p>Moves channel down in channel order list</p></body></html>"))
        self.adv_settings_button.setText(_translate("AcquisitionSettingsDialog", "Advanced Acquisition Settings"))
        self.adv_settings_label.setText(_translate("AcquisitionSettingsDialog", "Advanced Settings"))
