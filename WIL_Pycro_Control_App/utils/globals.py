"""
Holds constants for units and unit conversions, methods for important calculations
that are made throughout the program, as well as some directory methods. 
"""

import numpy as np
import os
import shutil

#unit conversions
M_TO_UM = 10**6
M_TO_MM = 10**3
S_TO_MS = 10**3
B_TO_MB = 1/10**6
MB_TO_B = 10**6
MB_TO_GB = 1/10**3
UM_TO_MM = 1/10**3
MM_TO_UM = 10**3
MS_TO_S = 1/10**3
MIN_TO_S = 60
S_TO_MIN = 1/60
S_IN_MIN = 60
TO_TENTHS = 10

def z_stack_speed_to_exposure(stage_speed) -> float:
    return 1/stage_speed*S_TO_MS


def framerate_to_exposure(framerate) -> float:
    return 1/framerate*S_TO_MS


def exposure_to_framerate(exposure) -> float:
    return 1/(exposure*MS_TO_S)


def value_in_range(value, bot, top):
    """
    returns value if bot < value < top, bot if value <= bot, and top if value => top.
    """
    return max(min(top, value), bot)


def get_str_from_float(value: float, num_decimals: int) -> str:
    return f"%.{num_decimals}f" % value


def swap_list_elements(lst, index_1, index_2):
    lst[index_1], lst[index_2] = lst[index_2], lst[index_1]


#directory methods
def get_unique_directory(dir: str) -> str:
    """
    returns save_path with "_i" appended where i is the first integar such that save_path is unique.
    """
    i = 1
    while os.path.isdir(dir):
        dir = dir.strip(f"_{i-1}") + f"_{i}"
        i += 1
    return dir


def get_free_mb_at_directory(dir: str) -> int:
    """
    returns number of available megabytes at directory specified by dir
    """
    return shutil.disk_usage(dir)[2]*B_TO_MB


def is_enough_space(required_mb: float, dir: str) -> bool:
    """ 
    returns True if number of MB available at dir is greater than required_mb
    """
    free_bytes = get_free_mb_at_directory(dir)
    return free_bytes > required_mb


def move_files_to_parent(child_dir):
    try:
        for filename in os.listdir(child_dir):
            shutil.move(f"{child_dir}/{filename}", os.path.dirname(child_dir))
        os.rmdir(child_dir)
    except:
        pass
    os.rename