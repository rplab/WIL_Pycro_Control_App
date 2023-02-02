"""
This module holds all custom exceptions.
"""

class AbortFlag():
    """
    Class used as a flag during acquisition to cause acquisition abort.
    """
    abort = False


class AbortAcquisitionException(Exception):
    """
    Raised when acquisition is aborted.
    """
    pass


class GeneralHardwareException(Exception):
    """
    General hardware exception for the general exception handling function.
    """
    pass


class CameraTimeoutException(Exception):
    """
    This was created for when the camera would unexpectedly get stuck during an acquisition. This
    is mainly an artifact from when image acquisitions would crash for apparently no reason (it ended up
    being a Windows 7 issues). This and all of the related implementation could probably be removed (I'm saying 
    this on 11/13/2022) if there's a reason to in the future.
    """
    pass
