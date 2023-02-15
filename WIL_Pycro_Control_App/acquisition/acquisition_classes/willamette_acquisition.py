import logging
import threading
import os
import views
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QApplication
from acquisition.acquisition_classes.abc_acquisition import AbstractAcquisition
from acquisition.acquisition_sequences import TimeSampAcquisition, SampTimeAcquisition
from hardware import stage, camera, plc
from models.acquisition.acquisition_user_data import AcquisitionSettings, AcquisitionOrder
from models.acquisition.acquisition_directory import AcquisitionDirectory
from utils import config, exceptions
from utils.pycro import core, studio

class Willamette_Acquisition(AbstractAcquisition):
    def _init_hardware(self):
        core.stop_sequence_acquisition()
        core.clear_circular_buffer()
        core.set_shutter_open(False)
        core.set_auto_shutter(True)
        stage.reset_joystick()
        plc.init_plc_state()

    def _write_settings_to_config(self):
        self._acq_settings.write_to_config()