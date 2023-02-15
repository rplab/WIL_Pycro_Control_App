import logging
from abc import ABC, abstractmethod
from hardware.exceptions_handle import general_exception_handle
from utils.pycro import studio, core


class AbstractCamera(ABC):
    _logger : logging.Logger

    MAX_EXPOSURE : float
    MIN_EXPOSURE : float

    @abstractmethod
    def default_mode(cls, exposure:int):
        pass

    CAM_NAME : str = core.get_camera_device()
    _WAIT_FOR_IMAGE_MS : float = 0.1
    DEFAULT_EXPOSURE : float = 20
    
    @classmethod
    def set_property(cls, property_name: str, value):
        """
        Sets given camera property name to value
        """
        core.set_property(cls.CAM_NAME, property_name, value)

    @classmethod
    def wait_for_camera(cls):
        core.wait_for_device(cls.CAM_NAME)

    @classmethod
    def start_sequence_acquisition(cls, num_frames: int):
        """
        Starts continuous sequence acquisition of number of images specified by num_frames.
        """
        def start_sequence_acquisition():
            #start_sequence_acquisition takes the arguments (long numImages, double intervalMs, bool stopOnOverflow)
            core.start_sequence_acquisition(num_frames, 0, True)
            cls._logger.info(f"Started sequence acquistiion of {num_frames} frames")
        
        return general_exception_handle(start_sequence_acquisition, cls._logger)

    @classmethod
    def snap_image(cls):
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
                core.sleep(cls._WAIT_FOR_IMAGE_MS)

            cls._logger.info(f"Snapped image")

        return general_exception_handle(snap_image, cls._logger)

    @classmethod
    def stop_live_acquisition(cls):
        """
        Turns live mode off in Micro-Manager, stopping live acquisition.
        """
        def stop_camera_acquisition():
            core.wait_for_device(cls.CAM_NAME)
            studio.live().set_live_mode_on(False)
            cls._logger.info(f"Stopped live acquisition")
        
        return general_exception_handle(stop_camera_acquisition, cls._logger)