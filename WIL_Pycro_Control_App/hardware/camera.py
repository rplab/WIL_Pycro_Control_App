"""
This module contains all methods that interact with the camera as well as methods that calculate relevant
values for it. Please read the documnetation for more information on specific settings and properties. 
The camera is connected through Micro-Manager, and so all its properties are set with the Micro-Manager API.
Please see pycro.py for more information on the Micro-Manager API.

I'm not sure if this is our exact PCO.Edge camera, but the timing diagrams/modes in this manual
are the same as ours:

https://www.tokyoinst.co.jp/product_file/file/PC07_man01_ja.pdf

Future changes:

- For now, since everything here is a constant, I didn't create a class to hold settings. If state is ever
added to this, should make a class to hold these.
"""

import logging
from hardware.exceptions_handle import general_exception_handle
from utils import globals
from utils.pycro import studio, core


_logger = logging.getLogger(__name__)

CAM_NAME = core.get_camera_device()
#Camera property names
_TRIGGER_MODE_PROP = "Triggermode"
_ACQUIRE_MODE_PROP = "Acquiremode"

#Camera properties
CAM_NAME = core.get_camera_device()
_DEFAULT_ACQUIRE_MODE = "Internal"
_DEFAULT_TRIGGER_MODE = "Software"
_Z_STACK_ACQUIRE_MODE = "External"
_Z_STACK_TRIGGER_MODE = "External"
_WAIT_FOR_IMAGE_MS = 0.1
DEFAULT_EXPOSURE = 20
#Can't seem to figure out what the max or min is for PCO. Isn't clear in documentation.
MAX_EXPOSURE = 2000
MIN_EXPOSURE = .010


def set_property(property_name: str, value):
    """
    Sets given camera property name to value
    """
    core.set_property(CAM_NAME, property_name, value)


def wait_for_camera():
    core.wait_for_device(CAM_NAME)


def default_mode(exposure:int):
    """
    Sets the camera properties to its default properties. 
    
    Currently, this sets the trigger mode to Internal and sets the 
    exposure to the default exposure set in MMHardwareCommands.

    Parameters:
    
    exposure:int - exposure time in ms
    """
    def default_mode():
        wait_for_camera()
        core.stop_sequence_acquisition()
        studio.live().set_live_mode_on(False)
        set_property(_TRIGGER_MODE_PROP, _DEFAULT_TRIGGER_MODE)
        set_property(_ACQUIRE_MODE_PROP, _DEFAULT_ACQUIRE_MODE)
        core.set_exposure(exposure)

    general_exception_handle(default_mode, _logger)


def z_stack_mode(exposure:int):
        """
        Sets the camera properties for a z-stack.

        Currently, only changes the trigger mode to external and changes
        the exposure time according to the parameters z_scan+_speed and exposure.

        Parameters:

        exposure:int - Sets the exposure time for scan, unless larger than
        max exposure time

        z_stack_speed:float - Used in determining max exposure time for scan
        """
        def z_stack_mode():
            wait_for_camera()
            #Stops acquisition of camera and turns live capture mode off
            #so that properties can be set.
            core.stop_sequence_acquisition()
            studio.live().set_live_mode_on(False)
            #exposure is set to a maximum (1/z_scan - 1) so pulses aren't
            #missed by the camera during scan. If a pulse is sent while the
            #camera is already taking an image, it will be skipped. 
            core.set_exposure(exposure)
            set_property(_TRIGGER_MODE_PROP, _Z_STACK_TRIGGER_MODE)
            set_property(_ACQUIRE_MODE_PROP, _Z_STACK_ACQUIRE_MODE)
        
        general_exception_handle(z_stack_mode, _logger)

def start_sequence_acquisition(num_frames: int):
    """
    Starts continuous sequence acquisition of number of images specified by num_frames.
    """
    def start_sequence_acquisition():
        #start_sequence_acquisition takes the arguments (long numImages, double intervalMs, bool stopOnOverflow)
        core.start_sequence_acquisition(num_frames, 0, True)
    
    return general_exception_handle(start_sequence_acquisition, _logger)


def snap_image():
    """
    Snaps an image with the camera. Image is then put in circular buffer where it can be grabbed with
    utils.pycro.pop_next_image(), which will return the image as a Micro-Manager image object.
    """
    def snap_image():
        #Originally when I scripted with MM, I would just use the snap() method in the studio.acquisition class, 
        # but this doesn't work with lsrm for some reason.
        core.start_sequence_acquisition(1, 0, True)
        #waits until image is actually in buffer. 
        while not core.get_remaining_image_count():
            core.sleep(_WAIT_FOR_IMAGE_MS)

    return general_exception_handle(snap_image, _logger)


def stop_live_acquisition():
    """
    Turns live mode off in Micro-Manager, stopping live acquisition.
    """
    def stop_camera_acquisition():
        core.wait_for_device(CAM_NAME)
        studio.live().set_live_mode_on(False)
    
    return general_exception_handle(stop_camera_acquisition, _logger)
