import logging
import numpy as np
from hardware import plc
from hardware.exceptions_handle import general_exception_handle
from utils import globals
from utils.pycro import core

class AbstractStage():
    _logger : logging.Logger

    #"abstract attributes" Interpreter will throw attribute error if the following aren't defined.
    STAGE_SERIAL_LABEL : str
    X_SERIAL_LABEL : str
    Y_SERIAL_LABEL : str
    Z_SERIAL_LABEL : str
    _INITIALIZE_SCAN_COMMAND : str
    _START_SCAN_COMMAND  : str
    _JOYSTICK_AXIS_RESET_COMMAND : str
    _JOYSTICK_Z_SPEED_COMMAND : str

    XY_STAGE_NAME : str = core.get_xy_stage_device()
    Z_STAGE_NAME : str = core.get_focus_device()

    _SERIAL : str = "SerialCommand"
    _SERIAL_NUM_DECIMALS : int = 6
    _JOYSTICK_ENABLE : str = "J X+ Y+ Z+"
    _JOYSTICK_Z_SPEED : str = "JSSPD Z=50"

    _DEFAULT_STAGE_SPEED_UM_PER_S : int = 1000
    #um buffer added to SCAN command so that camera takes enough images
    _BASE_Z_STACK_BUFFER : int = 2
    #number of um per um increase in buffer. Found empirically (reluctantly). See _get_z_stack_buffer().
    _UM_PER_UM_BUFFER = 92


    @classmethod
    def wait_for_xy_stage(cls):
        """
        Makes core wait for XY stage to become unbusy
        """
        core.wait_for_device(cls.XY_STAGE_NAME)
        cls._logger.info("Waiting for xy stage")

    @classmethod
    def wait_for_z_stage(cls):
        """
        Makes core wait for Z stage to become unbusy
        """
        core.wait_for_device(cls.Z_STAGE_NAME)
        cls._logger.info("Waiting for z stage")

    @classmethod
    def set_x_stage_speed(cls, speed):
        """
        Sets x-stage speed

        ### Parameters:

        #### x_speed
            stage speed in um/s
        """
        def set_x_stage_speed():
            cls.wait_for_xy_stage()
            #Since X and Z stages are swapped, must set Z-axis speed for X-axis speed change.
            cls.send_serial_command_to_stage(f"SPEED {cls.X_SERIAL_LABEL}={round(speed*globals.UM_TO_MM, cls._SERIAL_NUM_DECIMALS)}")
            cls._logger.info(f"x stage speed set to {speed} um/s")

        general_exception_handle(set_x_stage_speed, cls._logger)

    @classmethod
    def set_y_stage_speed(cls, speed):
        """
        Sets y-stage speed

        ### Parameters:

        #### x_speed
            stage speed in um/s
        """
        def set_y_stage_speed():
            cls.wait_for_xy_stage()
            cls.send_serial_command_to_stage(f"SPEED {cls.Y_SERIAL_LABEL}={round(speed*globals.UM_TO_MM, cls._SERIAL_NUM_DECIMALS)}")
            cls._logger.info(f"y stage speed set to {speed} um/s")

        general_exception_handle(set_y_stage_speed, cls._logger)

    @classmethod
    def set_z_stage_speed(cls, speed):
        """
        Sets z-stage speed

        ### Parameters:

        #### speed
            stage speed in um/s
        """
        def set_z_stage_speed():
            cls.wait_for_z_stage()
            cls.send_serial_command_to_stage(f"SPEED {cls.Z_SERIAL_LABEL}={round(speed*globals.UM_TO_MM, cls._SERIAL_NUM_DECIMALS)}")
            cls._logger.info(f"z stage speed set to {speed} um/s")
        general_exception_handle(set_z_stage_speed, cls._logger)

    @classmethod
    def initialize_scan(cls, start_z: int, end_z: int, scan_speed):
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
        def initialize_scan():
            #SCAN command sometimes causes the stage properties to bug out, so joystick is reset
            #and ensync position is set before every scan just in case.
            cls.reset_joystick()
            cls.set_ensync_position()

            corrected_speed = plc.get_true_z_stack_stage_speed(scan_speed)
            cls.set_z_stage_speed(corrected_speed)

            cls._send_scan_setup_commands(start_z, end_z)
            cls._logger.info("scan parameters have been set")
            return corrected_speed
        
        return general_exception_handle(initialize_scan, cls._logger)

    #scan_setup helpers
    @classmethod
    def _send_scan_setup_commands(cls, start_z, end_z):
        scan_r_command = cls._get_scan_r_command(start_z, end_z)
        cls.send_serial_command_to_stage(cls._INITIALIZE_SCAN_AXES)
        cls.send_serial_command_to_stage(scan_r_command)

    @classmethod
    def _get_scan_r_command(cls, start_z, end_z):
        start_z_mm = round(start_z*globals.UM_TO_MM, cls._SERIAL_NUM_DECIMALS)
        end_z_mm = round(cls._get_end_z_position(start_z, end_z)*globals.UM_TO_MM, cls._SERIAL_NUM_DECIMALS)
        return f"SCANR X={start_z_mm} Y={end_z_mm}"

    @classmethod
    def _get_end_z_position(cls, start_z, end_z):
        buffer = cls._get_z_stack_buffer(start_z, end_z)
        if start_z < end_z:
            end = end_z + buffer
        else:
            end = end_z - buffer

        return end

    @classmethod
    def _get_z_stack_buffer(cls, start_z, end_z):
        #This buffer... oh this buffer. Essentially, the stage TTL signal that goes HIGH
        #while the stage is moving during the SCAN command does not stay HIGH long enough.
        #For every ~92 microns in a scan, you must add 1 um to the buffer to make sure the
        #TTL is HIGH long enough for the camera to take enough images. 
        z_stack_range = cls._get_z_stack_range(start_z, end_z)
        return cls._BASE_Z_STACK_BUFFER + int(np.floor(z_stack_range/cls._UM_PER_UM_BUFFER))

    @classmethod
    def _get_z_stack_range(cls, z_start, z_end):
        return abs(z_start - z_end)

    @classmethod
    def scan_start(cls):
        """
        Sends SCAN command to the ASI stage to begin scan based on
        the properties set with scan_setup().

        This command tends to reset some of the settings of the joystick,
        so generally it's a good idea to call reset_joystick() after the scan
        is over.
        """
        def scan_start():
            cls.wait_for_xy_stage()
            cls.wait_for_z_stage()
            cls.send_serial_command_to_stage(cls._START_SCAN)
            cls._logger.info("Scan started")
                
        return general_exception_handle(scan_start, cls._logger)

    @classmethod
    def move_stage(cls, x_pos, y_pos, z_pos):
        """
        Sets stage to the position specified by parameters x_pos, y_pos, z_pos (in um)
        """
        def move_stage():
            cls.set_x_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)
            cls.set_y_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)
            cls.set_z_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)

            #This section is to ensure capillaries don't hit the objective. These conditions
            #should be changed to match the geometry of the holder.
            current_x_position = cls.get_x_position()
            if current_x_position > x_pos:
                cls.set_z_position(z_pos)
                cls.wait_for_z_stage()
                cls.set_xy_position(x_pos, y_pos)
                cls.wait_for_xy_stage()
            else:
                cls.set_xy_position(x_pos, y_pos)
                cls.wait_for_xy_stage()
                cls.set_z_position(z_pos)
                cls.wait_for_z_stage()

            cls._logger.info(f"Stage position set to ({x_pos}, {y_pos}, {z_pos})")
            
        return general_exception_handle(move_stage, cls._logger)

    @classmethod
    def set_x_position(cls, x_pos):
        """
        Sets stage X-axis to x_pos (in um)
        """
        def set_x_position():
            cls.wait_for_xy_stage()
            cls.set_x_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)
            #ASI MOVE (M) command takes position in tenths of microns, so multiply by 10       
            cls.send_serial_command_to_stage(f"M {cls.X_SERIAL_LABEL}={int(x_pos)*globals.TO_TENTHS}")
            cls._logger.info(f"Stage x position set to {x_pos} um")

        return general_exception_handle(set_x_position, cls._logger)

    @classmethod
    def set_y_position(cls, y_pos):
        """
        Sets stage Y-axis to y_pos (in um)
        """
        def set_y_position():
            cls.wait_for_xy_stage()
            cls.set_y_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)      
            cls.send_serial_command_to_stage(f"M {cls.Y_SERIAL_LABEL}={int(y_pos)*globals.TO_TENTHS}")
            cls._logger.info(f"Stage y position set to {y_pos} um")

        return general_exception_handle(set_y_position, cls._logger)

    @classmethod
    def set_xy_position(cls, x_pos, y_pos):
        """
        Sets xy position of stage (in um). Setting both at the same time makes it so both stages will move at the same time. 
        """
        cls.set_x_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)
        cls.set_y_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)
        core.set_xy_position(x_pos, y_pos)
        cls._logger.info(f"Stage xy position set to ({x_pos}, {y_pos}) um")

    @classmethod
    def set_z_position(cls, z_pos):
        """
        Sets stage Z-axis to z_pos (in um)
        """
        def set_z_position():
            cls.wait_for_z_stage()
            cls.set_z_stage_speed(cls._DEFAULT_STAGE_SPEED_UM_PER_S)      
            core.set_position(cls.Z_STAGE_NAME, z_pos)
            cls._logger.info(f"Stage z position set to {z_pos} um")

        return general_exception_handle(set_z_position, cls._logger)

    @classmethod
    def get_x_position(cls) -> int:
        """
        Retrieves current X-position from stage and returns it
        """
        def get_x_position():
            cls.wait_for_xy_stage()
            x_pos = int(core.get_x_position(cls.XY_STAGE_NAME))
            cls._logger.info(f"Current stage x position: {x_pos} um")
            return x_pos

        return general_exception_handle(get_x_position, cls._logger)

    @classmethod
    def get_y_position(cls) -> int:
        """
        Retrieves current Y-position from stage and returns it
        """
        def get_y_position():
            cls.wait_for_xy_stage()
            y_pos = int(core.get_y_position(cls.XY_STAGE_NAME))
            cls._logger.info(f"Current stage y position: {y_pos} um")
            return y_pos
            
        return general_exception_handle(get_y_position, cls._logger)

    @classmethod
    def get_z_position(cls) -> int:
        """
        Retrieves current Z-position from stage and returns it
        """
        def get_z_position():
            cls.wait_for_z_stage()
            z_pos = int(core.get_position(cls.Z_STAGE_NAME))
            cls._logger.info(f"Current stage z position: {z_pos} um")
            return z_pos
        
        return general_exception_handle(get_z_position, cls._logger)

    @classmethod
    def reset_joystick(cls):
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
            cls.wait_for_xy_stage()
            cls.wait_for_z_stage()
            cls.send_serial_command_to_stage(cls._JOYSTICK_ENABLE)
            cls.send_serial_command_to_stage(cls._JOYSTICK_AXIS_RESET)
            cls.send_serial_command_to_stage(cls._JOYSTICK_Z_SPEED)
            cls._logger.info("Joystick has been reset")
        
        general_exception_handle(reset_joystick, cls._logger)
        
    @classmethod
    def set_ensync_position(cls):
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

        general_exception_handle(set_ensync_position, cls._logger)