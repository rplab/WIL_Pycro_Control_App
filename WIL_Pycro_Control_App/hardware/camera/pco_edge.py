import logging
from hardware.camera.abc_camera import AbstractCamera
from hardware.exceptions_handle import general_exception_handle
from utils.pycro import studio, core

class PCO_Edge(AbstractCamera):
    _logger = logging.getLogger(__name__)

    #Can't seem to find out what the max or min exposure time is for PCO. Isn't clear in documentation.
    MAX_EXPOSURE = 2000
    MIN_EXPOSURE = 1

    #property names
    _TRIGGER_MODE_PROP = "Triggermode"
    _ACQUIRE_MODE_PROP = "Acquiremode"
    
    #properties
    _DEFAULT_ACQUIRE_MODE = "Internal"
    _DEFAULT_TRIGGER_MODE = "Software"
    _Z_STACK_ACQUIRE_MODE = "External"
    _Z_STACK_TRIGGER_MODE = "External"

    def default_mode(exposure:int):
        """
        Sets the camera properties to its default properties. 
        
        Currently, this sets the trigger mode to Internal and sets the 
        exposure to the default exposure set in MMHardwareCommands.

        Parameters:
        
        exposure:int - exposure time in ms
        """
        def default_mode():
            PCO_Edge.wait_for_camera()
            core.stop_sequence_acquisition()
            studio.live().set_live_mode_on(False)
            PCO_Edge.set_property(PCO_Edge._TRIGGER_MODE_PROP, PCO_Edge._DEFAULT_TRIGGER_MODE)
            PCO_Edge.set_property(PCO_Edge._ACQUIRE_MODE_PROP, PCO_Edge._DEFAULT_ACQUIRE_MODE)
            core.set_exposure(exposure)

            PCO_Edge._logger.info(f"Camera set to default mode with exposure time {exposure} ms")

        general_exception_handle(default_mode, PCO_Edge._logger)


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
            PCO_Edge.wait_for_camera()
            #Stops acquisition of camera and turns live capture mode off
            #so that properties can be set.
            core.stop_sequence_acquisition()
            studio.live().set_live_mode_on(False)
            #exposure is set to a maximum (1/z_scan - 1) so pulses aren't
            #missed by the camera during scan. If a pulse is sent while the
            #camera is already taking an image, it will be skipped. 
            core.set_exposure(exposure)
            PCO_Edge.set_property(PCO_Edge._TRIGGER_MODE_PROP, PCO_Edge._Z_STACK_TRIGGER_MODE)
            PCO_Edge.set_property(PCO_Edge._ACQUIRE_MODE_PROP, PCO_Edge._Z_STACK_ACQUIRE_MODE)

            PCO_Edge._logger.info(f"Camera set to z-stack mode with exposure time {exposure} ms")
        
        general_exception_handle(z_stack_mode, PCO_Edge._logger)
