"""
This import scheme sucks ass but intellisense wasn't working by just importing views,
so for now this is the way.
"""

from PyQt5 import QtWidgets
from views.abort_dialog import Ui_AbortDialog
from views.acquisition_dialog import Ui_AcquisitionDialog
from views.acquisition_order_dialog import Ui_AcquisitionOrderDialog
from views.acquisition_settings_dialog import Ui_AcquisitionSettingsDialog
from views.acquisitions_regions_dialog import Ui_AcquisitionRegionsDialog
from views.advanced_settings_dialog import Ui_AdvancedSettingsDialog
from views.main_window import Ui_MainWindow


class AbortDialog(QtWidgets.QDialog, Ui_AbortDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AcquisitionDialog(QtWidgets.QDialog, Ui_AcquisitionDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AcquisitionOrderDialog(QtWidgets.QDialog, Ui_AcquisitionOrderDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AcquisitionSettingsDialog(QtWidgets.QDialog, Ui_AcquisitionSettingsDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AcquisitionRegionsDialog(QtWidgets.QDialog, Ui_AcquisitionRegionsDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class AdvancedSettingsDialog(QtWidgets.QDialog, Ui_AdvancedSettingsDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class BrowseDialog(QtWidgets.QFileDialog):
    def __init__(self):
        super().__init__()
        
