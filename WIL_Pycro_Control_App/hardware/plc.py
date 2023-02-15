import logging
import numpy as np
from hardware.exceptions_handle import general_exception_handle
from utils import globals
from utils.pycro import core

_logger = logging.getLogger(__name__)

#device names
PLC_NAME = "PLogic:E:36"

#PLC property names
_POINTER_POSITION = "PointerPosition"
_EDIT_CELL_TYPE = "EditCellCellType"
_EDIT_CELL_CONFIG = "EditCellConfig"
_EDIT_CELL_INPUT_1 = "EditCellInput1"
_EDIT_CELL_INPUT_2 = "EditCellInput2"

#PLC element values
_VAL_INPUT = "0 - input"
_VAL_CONSTANT = "0 - constant"
_VAL_OUTPUT = "2 - output (push-pull)"
_VAL_AND = "5 - 2-input AND"
_VAL_OR = "6 - 2-input OR"
_VAL_ONE_SHOT = "8 - one shot"
_VAL_DELAY = "9 - delay"

#PLC element addresses
_ADDR_CLK = 192
_ADDR_BNC_1 = 33
_ADDR_STAGE_TTL= 34 #BNC port 2 on PLC
_ADDR_DELAY_1 = 1
_ADDR_OR = 2
_ADDR_AND = 3
_ADDR_DELAY_2 = 4
_ADDR_ONE_SHOT = 5
_ADDR_CONSTANT = 6

#PLC properties
_CLOCK_TICKS_PER_MS = 4
_TRIGGER_PULSE_WIDTH = 3*_CLOCK_TICKS_PER_MS
_PLC_CONSTANT_STATE = 1


#PLC commands
def wait_for_plc():
    core.wait_for_device(PLC_NAME)


def init_plc_state():
    """
    Initializes PLC circuit for use in z-stack acquisition and lsrm.

    The PLC (programmable logic card) is used to create logic circuits through software.
    There are a couple different ways to set up its elements. The method used in this program
    is the pointer system. Essentially, you set the pointer to the element you want to create/edit,
    set those properties, and then set the pointer to the next element.
    
    Please see the following for more information on how this works:

    http://www.asiimaging.com/downloads/manuals/Programmable_Logic_Card.pdf

    The circuit here creates a pulse matching the stage speed and step size during 
    a z-stack. This pulse is sent to the camera as an external trigger. If the stage
    scan speed is set to 30 um/s and the step size is 1 um, then the PLC output
    will pulse at 30 Hz. If the step size is 2 um, it will instead pulse at 15 Hz.

    Note that since the clock of the PLC runs at 4kHz, 1 ms is equal to 4 clock ticks,
    and so values in ms sent to the PLC must be multiplied by 4.

    For a full realization of this circuit, please see the developer's guide
    """
    def init_plc_state():
        #waiting for device is a common occurance just to make sure
        #device isn't busy with other tasks while setting properties
        wait_for_plc()
        #The frame interval is just the interval between pulses, determined
        #by the step size and scan speed. The values passed here are just the default
        #step size and z_scan_speed (didn't want an unnecessary import)
        frame_interval = _get_frame_interval(step_size=1, z_scan_speed=30)
        
        _set_plc_cell(_ADDR_STAGE_TTL, _VAL_INPUT, 0, 0, 0)
        _set_plc_cell(_ADDR_DELAY_1, _VAL_DELAY, 0, _ADDR_STAGE_TTL, _ADDR_CLK)
        _set_plc_cell(_ADDR_OR, _VAL_OR, 0, _ADDR_DELAY_1, _ADDR_DELAY_2)
        _set_plc_cell(_ADDR_AND, _VAL_AND, 0, _ADDR_OR, _ADDR_STAGE_TTL)
        _set_plc_cell(_ADDR_DELAY_2, _VAL_DELAY, frame_interval*_CLOCK_TICKS_PER_MS, _ADDR_AND, _ADDR_CLK)
        _set_plc_cell(_ADDR_ONE_SHOT, _VAL_ONE_SHOT, _TRIGGER_PULSE_WIDTH, _ADDR_AND, _ADDR_CLK)
        _set_plc_cell(_ADDR_BNC_1, _VAL_OUTPUT, _ADDR_ONE_SHOT, 0, 0)
        _set_plc_cell(35, _VAL_OUTPUT, _ADDR_STAGE_TTL, 0, 0)
        _set_plc_cell(36, _VAL_OUTPUT, _ADDR_STAGE_TTL, 0, 0)

        _logger.info(f"PLC initialized with frame interval {frame_interval} ms")

    return general_exception_handle(init_plc_state, _logger)


def set_plc_for_z_stack(step_size: int, stage_scan_speed):
    """
    Sets the frame interval of the PLC for use during z-stack acquisition. 
    
    This is intended to be used after initialize_plc_for_z_stack() to update the frame interval
    to match the current step size. All other propertes set in initialize_plc_for_z_stack() 
    will remain the same.

    ### Parameters:

    #### step_size : int
        z-stack step_size in um

    #### z_scan_speed
        z-stack scan speed in mm/s
    """
    def set_plc_for_z_stack():
        wait_for_plc()

        frame_interval = _get_frame_interval(step_size, stage_scan_speed)

        _set_plc_pointer_position(_ADDR_DELAY_1)
        _edit_plc_cell_input_1(_ADDR_STAGE_TTL)

        _set_plc_pointer_position(_ADDR_AND)
        _edit_plc_cell_input_2(_ADDR_STAGE_TTL)

        _set_plc_pointer_position(_ADDR_DELAY_2)
        #_edit_plc_cell_config(_get_frame_interval(step_size, stage_scan_speed))
        _edit_plc_cell_config(frame_interval*_CLOCK_TICKS_PER_MS)

        _set_plc_cell(35, _VAL_OUTPUT, _ADDR_STAGE_TTL, 0, 0)
        _set_plc_cell(36, _VAL_OUTPUT, _ADDR_STAGE_TTL, 0, 0)

        _logger.info(f"PLC set for z-stack with frame interval of {frame_interval} ms")

    return general_exception_handle(set_plc_for_z_stack, _logger)

def set_plc_for_continuous_lsrm(framerate: int):
    """
    Initializes PLC circuit to send continuouse pulses at set intervals determined
    by the framerate prameter.

    On the Klamath light sheet, this is used for lightsheet readout mode when the stage
    isn't triggering the PLC, such as videos and snaps in lightsheet readout mode.

    ### Parameters:

    #### framerate : int
        framerate of lightsheet readout mode.
    """
    def set_plc_for_continuous_lsrm():
        wait_for_plc()
        frame_interval = _get_frame_interval_from_framerate(framerate)

        _set_plc_pointer_position(_ADDR_DELAY_1)
        _edit_plc_cell_input_1(_ADDR_CONSTANT)

        _set_plc_pointer_position(_ADDR_AND)
        _edit_plc_cell_input_2(_ADDR_CONSTANT)

        _set_plc_pointer_position(_ADDR_DELAY_2)
        _edit_plc_cell_config(frame_interval*_CLOCK_TICKS_PER_MS)
        
        _set_plc_pointer_position(_ADDR_CONSTANT)
        _edit_plc_cell_type(_VAL_CONSTANT)
        _edit_plc_cell_config(_PLC_CONSTANT_STATE)

        _logger.info(f"PLC set for continuous LSRM with frame interval of {frame_interval} ms")

    return general_exception_handle(set_plc_for_continuous_lsrm, _logger)


#PLC helpers
def _set_plc_cell(address, cell_type, config_value, input_1, input_2):
    """
    Sets PLC cell at given address with given properties
    """
    _set_plc_pointer_position(address)
    _edit_plc_cell_type(cell_type)
    _edit_plc_cell_config(config_value)
    _edit_plc_cell_input_1(input_1)
    _edit_plc_cell_input_2(input_2)


def _set_plc_pointer_position(address):
    """
    Sets pointer position to address. Allows editing of element at address (or creation if it doesn't exist).
    """
    core.set_property(PLC_NAME, _POINTER_POSITION, address)


def _edit_plc_cell_type(type):
    """
    Edit cell type of element at current pointer position. Cell type is the type of logic gate, i.e. OR, AND, 
    ONESHOT, DELAY, etc.
    """
    core.set_property(PLC_NAME, _EDIT_CELL_TYPE, type)


def _edit_plc_cell_config(value):
    """
    Edit cell config of element at current pointer position. Generally, config is the most important value
    for configuring an element.
    """
    core.set_property(PLC_NAME, _EDIT_CELL_CONFIG, value)


def _edit_plc_cell_input_1(value):
    """
    Edit input_1 element at current pointer position. What this actually changes depends on the gate type.
    """
    core.set_property(PLC_NAME, _EDIT_CELL_INPUT_1, value)


def _edit_plc_cell_input_2(value):
    """
    Edit input_2 element at current pointer position. What this actually changes depends on the gate type.
    """
    core.set_property(PLC_NAME, _EDIT_CELL_INPUT_2, value)


def _get_frame_interval(step_size: int, z_scan_speed) -> int:
    """
    Calculates frame_interval from step_size and z_scan_speed and returns it.
    """
    #ceil is so the interval is greater than the framerate set in lsrm, which makes it so that 
    #pulses aren't missed by the camera.
    return np.ceil((step_size/(z_scan_speed*globals.UM_TO_MM))*_CLOCK_TICKS_PER_MS)/_CLOCK_TICKS_PER_MS


def _get_frame_interval_from_framerate(framerate):
    """
    Really similar to globals.framerate_to_exposure(), except uses np.ceil instead of floor.
    """
    return np.ceil((1/framerate*globals.S_TO_MS)*_CLOCK_TICKS_PER_MS)/_CLOCK_TICKS_PER_MS


def get_true_z_stack_stage_speed(z_scan_speed):
    return round(1/(_get_frame_interval(1, z_scan_speed))*globals.MM_TO_UM, 3)
