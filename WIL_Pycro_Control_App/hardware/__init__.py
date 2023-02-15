import contextlib
from hardware.camera.pco_edge import PCO_Edge
from hardware.stage.willamette import Willamette_Stage
from hardware import plc
from utils import exceptions

#set camera to default settings
camera = PCO_Edge
with contextlib.suppress(exceptions.GeneralHardwareException):
    camera.default_mode(camera.DEFAULT_EXPOSURE)

#Initialize stage to default state.
stage = Willamette_Stage
with contextlib.suppress(exceptions.GeneralHardwareException):
    stage.set_x_stage_speed(stage._DEFAULT_STAGE_SPEED_UM_PER_S)
    stage.set_y_stage_speed(stage._DEFAULT_STAGE_SPEED_UM_PER_S)
    stage.set_z_stage_speed(stage._DEFAULT_STAGE_SPEED_UM_PER_S)
    stage.reset_joystick()

#Initializes plc to default state.
with contextlib.suppress(exceptions.GeneralHardwareException):
    plc.init_plc_state()
