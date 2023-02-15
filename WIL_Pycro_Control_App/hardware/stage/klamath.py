import logging
from hardware.stage.abc_stage import AbstractStage

class Klamath_Stage(AbstractStage):
    _logger = logging.getLogger(__name__)
    
    #device names
    STAGE_SERIAL_LABEL = "TigerCommHub"
    X_AXIS_LABEL = "X"
    Y_AXIS_LABEL = "Y"
    Z_AXIS_LABEL = "Z"
    _INITIALIZE_SCAN_COMMAND = "2 SCAN Y=0 Z=0"
    _START_SCAN_COMMAND = "2 SCAN"
    _JOYSTICK_AXIS_RESET_COMMAND = ""
    _JOYSTICK_Z_SPEED_COMMAND = ""
