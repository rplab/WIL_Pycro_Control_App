import contextlib
from hardware import camera, plc
from utils import exceptions

#Initializes camera to default settings.
with contextlib.suppress(exceptions.GeneralHardwareException):
    camera.default_mode(camera.DEFAULT_EXPOSURE)

#Initializes plc to default state.
with contextlib.suppress(exceptions.GeneralHardwareException):
    plc.init_plc_state()
