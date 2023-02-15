import logging
from hardware.camera.abc_camera import AbstractCamera
from hardware.exceptions_handle import general_exception_handle
from utils import globals
from utils.pycro import core

class Hamamatsu(AbstractCamera):
    _logger = logging.getLogger(__name__)

    MAX_EXPOSURE = 10000
    MIN_EXPOSURE = 1

    #property names
    _SENSOR_MODE_PROP = "SENSOR MODE"
    _TRIGGER_POLARITY_PROP = "TriggerPolarity"
    _TRIGGER_SOURCE_PROP = "TRIGGER SOURCE"
    _TRIGGER_ACTIVE_PROP = "TRIGGER ACTIVE"
    _ILI_PROP = "INTERNAL LINE INTERVAL"

    #properties
    _AREA_SENSOR_MODE = "AREA"
    _LSRM_SENSOR_MODE = "PROGRESSIVE"
    _NEGATIVE_POLARITY = "NEGATIVE"
    _POSITIVE_POLARITY= "POSITIVE"
    _INTERNAL_SOURCE = "INTERNAL"
    _EXTERNAL_SOURCE = "EXTERNAL"
    _EDGE_TRIGGER = "EDGE"
    _SYNC_READOUT = "SYNCREADOUT"
    READOUT_PER_PIXEL_ROW_S = 9.74436*10**-6
    NUM_LINES_DELAY = 10

    def default_mode(exposure: float):
        """
        Sets the camera properties to its default properties. 
        
        Currently, this sets the trigger mode to Internal and sets the exposure time to the exposure provided.

        ### Parameters:
        
        #### exposure : int
            exposure time in ms. read the Hamamatsu documentation for what exposure
            times are allowed.
        """
        def default_mode():
            Hamamatsu.stop_live_acquisition()
            Hamamatsu.set_property(Hamamatsu._SENSOR_MODE_PROP, Hamamatsu._AREA_SENSOR_MODE)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_POLARITY_PROP, Hamamatsu._NEGATIVE_POLARITY)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_SOURCE_PROP, Hamamatsu._INTERNAL_SOURCE)
            #set_property(_TRIGGER_ACTIVE_PROP, _EDGE_TRIGGER)
            core.set_exposure(exposure)

        return general_exception_handle(default_mode, Hamamatsu._logger)
    
    def z_stack_mode(cls, exposure: float):
        def z_stack_mode():
            Hamamatsu.stop_live_acquisition()
            Hamamatsu.set_property(Hamamatsu._SENSOR_MODE_PROP, Hamamatsu._AREA_SENSOR_MODE)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_POLARITY_PROP, Hamamatsu._POSITIVE_POLARITY)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_SOURCE_PROP, Hamamatsu._EXTERNAL_SOURCE)
            core.set_exposure(exposure)
        
        return general_exception_handle(z_stack_mode, Hamamatsu._logger)

    def light_sheet_readout_mode(ili: float, num_lines: int):
        """
        This is fundamentally different from DSLM properties in two ways. 
        The sensor mode is set to progressive and we need to set an internal
        line interval. Please read the lightsheet readout mode guide for a 
        full explanation of this mode.

        Essentially, this is the LSRM analog of the set_dslm_camera_properties()
        method.

        parameters:

        ili : float 
        Internal Line Interval. Sets the readout sweeping frequency of lsrm.

        num_lines : int
        sets the number of lines that are active at one time. Essentially sets the exposure
        of each line equal to num_lines.
        """
        def light_sheet_readout_mode():
            Hamamatsu.stop_live_acquisition()
            line_interval_ms = ili*globals.S_TO_MS
            Hamamatsu.set_property(Hamamatsu._SENSOR_MODE_PROP, Hamamatsu._LSRM_SENSOR_MODE)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_POLARITY_PROP, Hamamatsu._POSITIVE_POLARITY)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_SOURCE_PROP, Hamamatsu._EXTERNAL_SOURCE)
            Hamamatsu.set_property(Hamamatsu._TRIGGER_ACTIVE_PROP, Hamamatsu._EDGE_TRIGGER)
            Hamamatsu.set_property(Hamamatsu._ILI_PROP, line_interval_ms)
            core.set_exposure(line_interval_ms * int(num_lines))
        
        return general_exception_handle(light_sheet_readout_mode, Hamamatsu._logger)

    def edge_trigger_mode(desired_exposure, framerate) -> int:
        """
        Puts camera into edge trigger mode. Exposure time is limited by framerate, and so exposure time passed in
        may not be the actual exposure time set. See the Hamamatsu documentation for more details.

        Currently used during z-stacks where the desired exposure time is below 1/stage_speed. 

        ### Parameters:

        #### exposure : int
            desired Exposure time in ms. Read the Hamamatsu documentation on what exposure
            times are allowed.

        #### framerate : int
            framerate of camera.
        """
        def edge_trigger_mode():
            Hamamatsu.stop_live_acquisition()
            Hamamatsu.set_property(Hamamatsu._TRIGGER_ACTIVE_PROP, Hamamatsu._EDGE_TRIGGER)
            exp = Hamamatsu.get_edge_trigger_exposure(desired_exposure, framerate)
            core.set_exposure(exp)
            return exp
        
        return general_exception_handle(edge_trigger_mode, Hamamatsu._logger)


    def sync_readout_mode():
        """
        Sets the camera properties for a z-stack in normal galvo scanning mode
        (dslm() in galvo commands). Returns actual set exposure time.

        """
        def sync_readout_mode():
            Hamamatsu.stop_live_acquisition()
            Hamamatsu.set_property(Hamamatsu._TRIGGER_ACTIVE_PROP, Hamamatsu._SYNC_READOUT)
        
        return general_exception_handle(sync_readout_mode, Hamamatsu._logger)

    #helpers
    def get_edge_trigger_exposure(desired_exposure, framerate):
        """
        Takes desired exposure time and returns it if it's appropriate for edge trigger mode. If it's outside of the range
        of appropriate exposure times, returns closest limiting exposure. 
        
        The Hamamatsu documentation says that the maximum framerate is given by 1/(Vn/2*1H + Exp + 1H * 10) where Vn is the 
        number of lines (pixel rows), Exp is the exposure, and 1H is the readout of a single pixel row. From this, we can 
        solver for the exposure, which gives us max_exp = 1/framerate - readout_delay where readout_delay is the additional
        readout of pixel rows.
        
        Please see the framerate section of the Hamamatsu documentation for more details on this.
        """
        if not core.is_sequence_running():
            readout_delay = Hamamatsu.get_edge_trigger_readout(core.get_image_height())
            max_exposure = (1/framerate - readout_delay)*globals.S_TO_MS
            print(max_exposure)
            return globals.value_in_range(desired_exposure, Hamamatsu.MIN_EXPOSURE, max_exposure)
        return desired_exposure


    def get_edge_trigger_readout(image_height):
        """
        This is the readout time plus delay from the framerate calculation in the Hamamatsu documentation.
        Symbolocally, this is 1H*(Vn/2 + 10) where1 H is the readout of one single row and Vn is the number of pixel rows.
        """
        return Hamamatsu.READOUT_PER_PIXEL_ROW_S*(image_height/2 + Hamamatsu.NUM_LINES_DELAY)