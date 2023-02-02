import logging
import numpy as np
from hardware import plc
from hardware.exceptions_handle import general_exception_handle
from utils import globals
from utils.pycro import core

_logger = logging.getLogger(__name__)

#device names
ASI_XY_STAGE_NAME = "ASI-XYStage"
ASI_Z_STAGE_NAME = "XStage"
XY_STAGE_NAME = core.get_xy_stage_device()
Z_STAGE_NAME = core.get_focus_device()

#Stage serial properties
_SERIAL = "SerialCommand"
_SERIAL_NUM_DECIMALS = 6

#Stage properties
_DEFAULT_STAGE_SPEED_UM_PER_S = 1000
#um buffer added to SCAN command so that camera takes enough images
_BASE_Z_STACK_BUFFER = 2
#number of um per um increase in buffer. Found empirically (reluctantly).
_UM_PER_UM_BUFFER = 92
_BUFFER_THRESHOLD = 100
_INITIALIZE_SCAN = "SCAN X=1 Y=0 Z=0"
_START_SCAN = "SCAN"
_RESET_STAGE = "RESET"
_JOYSTICK_ENABLE = "J X+ Y+ Z+"
_JOYSTICK_AXIS_RESET = "J X=4 Y=3 Z=2"
_JOYSTICK_Z_SPEED = "JSSPD Z=50"
_X_ENSYNC = "ENSYNC X=5"
_Y_ENSYNC = "ENSYNC Y=5"
_Z_ENSYNC = "ENSYNC Z=5"


#Stage commands
def wait_for_xy_stage():
    """
    Makes core wait for XY stage to become unbusy
    """
    core.wait_for_device(XY_STAGE_NAME)

def wait_for_z_stage():
    """
    Makes core wait for Z stage to become unbusy
    """
    core.wait_for_device(Z_STAGE_NAME)

def send_serial_command_to_stage(serial_command):
    """
    Sends serial command to ASI Tiger Console. See the Tiger documentation for
    a list of serial commands.
    """
    core.wait_for_device(XY_STAGE_NAME)
    core.set_property(ASI_XY_STAGE_NAME, _SERIAL, serial_command)

def set_x_stage_speed(speed):
    """
    Sets x-stage speed

    ### Parameters:

    #### x_speed
        stage speed in um/s
    """
    def set_x_stage_speed():
        wait_for_xy_stage()
        #Since X and Z stages are swapped, must set Z-axis speed for X-axis speed change.
        send_serial_command_to_stage(f"SPEED Z={round(speed*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)}")

    general_exception_handle(set_x_stage_speed, _logger)


def set_y_stage_speed(speed):
    """
    Sets y-stage speed

    ### Parameters:

    #### x_speed
        stage speed in um/s
    """
    def set_y_stage_speed():
        wait_for_xy_stage()
        send_serial_command_to_stage(f"SPEED Y={round(speed*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)}")

    general_exception_handle(set_y_stage_speed, _logger)


def set_z_stage_speed(speed):
    """
    Sets z-stage speed

    ### Parameters:

    #### speed
        stage speed in um/s
    """
    def set_z_stage_speed():
        wait_for_z_stage()
        send_serial_command_to_stage(f"SPEED X={round(speed*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)}")

    general_exception_handle(set_z_stage_speed, _logger)


def scan_setup(start_z: int, end_z: int, scan_speed):
    """
    Performs setup for stage SCAN command. 
    
    Please read the ASI manual for more details on SCAN:
    http://www.asiimaging.com/downloads/manuals/Operations_and_Programming_Manual.pdf
    
        An ASI stage scan is achieved by doing the following:

    1. Scan properties are set as "2 SCAN Y=0 Z=0 F=0". This is simply
        to tell the stage what axis will be scanning. In our case, we're
        scanning along the z-axis
    2. Positions are set with SCANR X=[StartPosition] Y=[EndPosition]
        where positions are in units of mm. SCANR means raster scan.
    3. "SCAN" is sent. When the stage reaches the start position, the TTL 
        port on the stage goes high. This is what triggers the PLC to pulse. 
        Once it reaches the end position, the TTL goes low and the stage resets 
        to the start position.

    ### Parameters:

    #### start_z : int
        scan start position in um

    #### end_z : int
        scan end position in um

    #### scan_speed
        scan speed in um/s
    """
    def scan_setup():
        wait_for_xy_stage()
        wait_for_z_stage()
        #SCAN command sometimes causes the stage properties to bug out, so joystick is reset
        #and ensync position is set before every scan just in case.
        reset_joystick()
        set_ensync_position()

        z_stack_stage_speed = plc.get_true_z_stack_stage_speed(scan_speed)
        set_z_stage_speed(z_stack_stage_speed)

        #SCAN command takes positions in MM, so we must convert positions to mm.
        start = round(start_z*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)
        #This buffer... oh this buffer. Essentially, the stage TTL signal that goes HIGH
        #while the stage is moving during the SCAN command does not stay HIGH long enough.
        #For every ~92 microns in a scan, you must add 1 um to the buffer to make sure the
        #TTL is HIGH long enough for the camera to take enough images. 
        buffer = _calculate_z_stack_buffer(start_z, end_z)
        if start_z < end_z:
            end = round((end_z + buffer)*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)
        else:
            end = round((end_z - buffer)*globals.UM_TO_MM, _SERIAL_NUM_DECIMALS)

        scan_r_properties = f"SCANR X={start} Y={end}"
        send_serial_command_to_stage(_INITIALIZE_SCAN)
        send_serial_command_to_stage(scan_r_properties)
        return z_stack_stage_speed
    
    return general_exception_handle(scan_setup, _logger)


def _calculate_z_stack_buffer(z_start, z_end):
    z_stack_range = abs(z_start - z_end)
    return _BASE_Z_STACK_BUFFER + int(np.floor(z_stack_range/_UM_PER_UM_BUFFER))


def scan_start():
    """
    Sends SCAN command to the ASI stage to begin scan based on
    the properties set with scan_setup().

    This command tends to reset some of the settings of the joystick,
    so generally it's a good idea to call reset_joystick() after the scan
    is over.
    """
    def scan_start():
        wait_for_xy_stage()
        wait_for_z_stage()
        send_serial_command_to_stage(_START_SCAN)
            
    return general_exception_handle(scan_start, _logger)


def move_stage(x_pos, y_pos, z_pos):
    """
    Sets stage to the position specified by parameters x_pos, y_pos, z_pos (in um)
    """
    def move_stage():
        set_x_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)
        set_y_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)
        set_z_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)

        #This section is to ensure capillaries don't hit the objective. These conditions
        #should be changed to match the geometry of the holder.
        current_x_position = get_x_position()
        if current_x_position > x_pos:
            set_z_position(z_pos)
            wait_for_z_stage()
            set_xy_position(x_pos, y_pos)
            wait_for_xy_stage()
        else:
            set_xy_position(x_pos, y_pos)
            wait_for_xy_stage()
            set_z_position(z_pos)
            wait_for_z_stage()
        
    return general_exception_handle(move_stage, _logger)


def set_x_position(x_pos):
    """
    Sets stage X-axis to x_pos (in um)
    """
    def set_x_position():
        wait_for_xy_stage()
        set_x_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)
        #ASI MOVE (M) command takes position in tenths of microns, so multiply by 10       
        send_serial_command_to_stage(f"M Z={int(x_pos)*globals.TO_TENTHS}")

    return general_exception_handle(set_x_position, _logger)


def set_y_position(y_pos):
    """
    Sets stage Y-axis to y_pos (in um)
    """
    def set_y_position():
        wait_for_xy_stage()
        set_y_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)      
        send_serial_command_to_stage(f"M Y={int(y_pos)*globals.TO_TENTHS}")

    return general_exception_handle(set_y_position, _logger)


def set_xy_position(x_pos, y_pos):
    """
    Sets xy position of stage (in um). Setting both at the same time makes it so both stages will move at the same time. 
    """
    set_x_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)
    set_y_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)
    core.set_xy_position(x_pos, y_pos)


def set_z_position(z_pos):
    """
    Sets stage Z-axis to z_pos (in um)
    """
    def set_z_position():
        wait_for_z_stage()
        set_z_stage_speed(_DEFAULT_STAGE_SPEED_UM_PER_S)      
        core.set_position(Z_STAGE_NAME, z_pos)

    return general_exception_handle(set_z_position, _logger)


def get_x_position() -> int:
    """
    Retrieves current X-position from stage and returns it
    """
    def get_x_position():
        wait_for_xy_stage()
        return int(core.get_x_position(XY_STAGE_NAME))

    return general_exception_handle(get_x_position, _logger)


def get_y_position() -> int:
    """
    Retrieves current Y-position from stage and returns it
    """
    def get_y_position():
        wait_for_xy_stage()
        return int(core.get_y_position(XY_STAGE_NAME))
        
    return general_exception_handle(get_y_position, _logger)


def get_z_position() -> int:
    """
    Retrieves current Z-position from stage and returns it
    """
    def get_z_position():
        wait_for_z_stage()
        return int(core.get_position(Z_STAGE_NAME))
    
    return general_exception_handle(get_z_position, _logger)


def reset_joystick():
    """
    Sends commands to joystick to reset it to dsired state.

    The joystick tends to bug out after the SCAN command. This resets
    the joystick so that it works correctly. Essentially, "J X+ Y+ Z+" 
    re-enables the joystick axes, "J X=4 Y=3 Z=2" makes it so horizontal
    joystick movement moves the Z-axis and the knob moves the X-axis, and 
    "JSSPD Z=5" changes the speed of the joystick. 

    Please see the ASI MS-2000 documentation for more details on this command:

    http://www.asiimaging.com/downloads/manuals/Operations_and_Programming_Manual.pdf

    """
    def reset_joystick():
        wait_for_xy_stage()
        wait_for_z_stage()
        send_serial_command_to_stage(_JOYSTICK_ENABLE)
        send_serial_command_to_stage(_JOYSTICK_AXIS_RESET)
        send_serial_command_to_stage(_JOYSTICK_Z_SPEED)
    
    general_exception_handle(reset_joystick, _logger)


def reset_stage():
    """
    Resets current flash memory of Tiger console by sending "RESET" command to stage. Please see the ASI 
    documentation to see all the settings this resets. Most notably, it resets the origin to its 
    current position and the joystick settings. Used to be used on the Willamette setup because the 
    stage would bug out.

    DEPRECATED (Unless a different use comes up)
 
    """
    def reset_stage():
        send_serial_command_to_stage(_RESET_STAGE)
    
    general_exception_handle(reset_stage, _logger)
    

def set_ensync_position():
    """
    Sets stage ensync position to an unreachable position.

    This might not be necessary, but this sets the ensync position to a position (400mm, 400mm, 400mm)
    that the stage will never reach. The ensync position is a position that, if crossed, causes the TTL
    signal on the stage to go HIGH, which has the potential to mess with the TTL signal from the SCAN command
    during z-stacks.
    """
    def set_ensync_position():
        '''
        wait_for_xy_stage()
        wait_for_z_stage()
        send_serial_command_to_stage(_X_ENSYNC)
        send_serial_command_to_stage(_Y_ENSYNC)
        send_serial_command_to_stage(_Z_ENSYNC)
        '''
        pass

    general_exception_handle(set_ensync_position, _logger)
