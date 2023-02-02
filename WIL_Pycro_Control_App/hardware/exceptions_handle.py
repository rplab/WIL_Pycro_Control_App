import logging
from typing import Callable
from utils.exceptions import GeneralHardwareException


#TODO Test hardware for raise exceptions and add specific exception handling from exceptions raised in
#methods themselves.

def general_exception_handle(function: Callable, logger: logging.Logger):
    """
    Generic exception handler for all hardware functions.

    In each hardware function, a nested function with no arguments is defined
    with the actual function implementation, which is then passed to this 
    function to handle errors.

    ### Parameters:

    #### funct : Callable
        function to run exception handle on

    #### logger : logging.Logger
        logger to write info or exceptions to logs
    """
    function_name = function.__code__.co_name
    attempts = 2
    for exception_count in range(attempts):
        try:
            return_value = function()
        except Exception:
            message = f"Exception raised during {function_name}"
            if exception_count < attempts - 1:
                message += ", reattempting"
            logger.exception(message)
        else:
            logger.info(f"{function_name} completed")
            return return_value
    
    message = f"{__name__} {function_name} failed. Check device, its connection, and the logs."
    logger.info(message)
    print(message)
    raise GeneralHardwareException(message)