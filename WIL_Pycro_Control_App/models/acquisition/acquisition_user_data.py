"""
The "Model" part of the acquisition package. Contains all classes that hold properties to be used during image 
acquisition.

Notes:

- If adding a fish or region to these lists, use append unless you're replacing an element
at an index.

- All "exposure" attributes are units of ms and all "pos" attributes are in um.

- If new settings are needed in the future for acquisitions, I HIGHLY reccomend inheriting one of these already
created classes instead of adding functionality to them. This will ensure no required attributes are missing.

Future Changes:
- If more types of image acquisition modes are added, AcquisitionOrder will need to be
updated accordingly.

- More input validation could be added, especially for save paths and things like that.

- I hate this docstring format with a passion but it works alright with vscode. Should be updated in the future.

- Split up Region and AcquisitionSettings into multiple classes (or at least add dicts). Might be a bit too much work...
  
- consider using dataclass decorator for these. Would make it much pretty and field methods could be useful.
"""

import numpy as np
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
from hardware import camera
from utils import config, globals, pycro
from utils.pycro import core


class UserDataClass(ABC):
    @abstractmethod
    def write_to_config(self):
        """
        Write instance attributes to Config. Please see Config class in utils.
        """
        config.write_class(self)


class Region(UserDataClass):
    """
    Data class that stores properties that are specific to individual regions.

    ## Instance Attributes:

    #### x_pos : int 
        x_pos (in um)

    #### y_pos : int
        y_pos (in um)

    #### z_pos : int
        z_pos (in um)

    #### z_stack_bool : bool 
        If True, z-stacks will be enabled for the acquisition of this region.

    #### start_z_pos : int
        starting pos of z-stack (in um)

    #### end_z_pos : int
        end pos of z-stack (in um)

    #### step_size : int
        step size to be used during z-stack (in um)

    #### z_stack_channel_list : list[str]
        list of channels to be used for z-stack acquisition

    #### snap_bool : bool
        if True, snaps will be enabled for the acquisition of this region

    #### snap_exposure : int
        exposure time (in ms) to be used during snap

    #### snap_channel_list : list[str]
        list of channels to be used for snap acquisition

    #### video_bool : bool
        if True, snaps will be enabled for the acquisition of this region

    #### video_num_frames : int
        number of frames to be acquired in video acquisition

    #### video_exposure : int
        exposure time (in ms) to be used during video

    #### video_channel_list : list[str]
        list of channels to be used for video acquisition

    #### num_images : int
        number of images to be acquired at this region. set by update_num_images().

    ## Instance Methods

    update_num_images() - calculates number of images to be acquired for region instance and sets num_images to said 
    value.
    """
    x_pos: int = 0
    y_pos: int = 0
    z_pos: int = 0
    z_stack_enabled: bool = False
    z_stack_start_pos: int = 0
    z_stack_end_pos: int = 0
    z_stack_step_size: int = 1
    z_stack_channel_list: list[str] = []
    snap_enabled: bool = False
    snap_exposure: float = 20
    snap_channel_list: list[str] = []
    video_enabled: bool = False
    video_num_frames: int = 100
    video_exposure: float = 20
    video_channel_list: list[str] = []

    def __init__(self):
        self.x_pos: int = Region.x_pos
        self.y_pos: int = Region.y_pos
        self.z_pos: int = Region.z_pos
        self.z_stack_enabled: bool = Region.z_stack_enabled
        self.z_stack_start_pos: int = Region.z_stack_start_pos
        self.z_stack_end_pos: int = Region.z_stack_end_pos
        self.z_stack_step_size: int = Region.z_stack_step_size
        self.z_stack_channel_list: list[str] = deepcopy(Region.z_stack_channel_list)
        self.snap_enabled: bool = Region.snap_enabled
        self.snap_exposure: float = Region.snap_exposure
        self.snap_channel_list: list[str] = deepcopy(Region.snap_channel_list)
        self.video_enabled: bool = Region.video_enabled
        self.video_num_frames: int = Region.video_num_frames
        self.video_exposure: float = Region.video_exposure
        self.video_channel_list: list[str] = deepcopy(Region.video_channel_list)
        self.num_images: int = self.update_num_images()
    
    def update_num_images(self):
        num_z_stack_images = 0
        num_snap_images = 0
        num_video_images = 0
        if self.z_stack_enabled:
            self.get_z_stack_num_frames()
            num_z_stack_images = len(self.z_stack_channel_list)*self.z_stack_num_frames
        if self.snap_enabled:
            num_snap_images = len(self.snap_channel_list)
        if self.video_enabled:
            num_video_images = len(self.video_channel_list)*self.video_num_frames
        self.num_images = num_z_stack_images + num_snap_images + num_video_images
    
    def get_z_stack_num_frames(self):
        num_frames = int(np.ceil(abs(self.z_stack_end_pos - self.z_stack_start_pos)/self.z_stack_step_size))
        self.z_stack_num_frames = num_frames
        return num_frames

    def is_imaging_enabled(self):
        return (self.snap_enabled or self.video_enabled or self.z_stack_enabled)
    
    def write_to_config(self, fish_num, region_num):
        config.write_class(self, Region.config_section(fish_num, region_num))

    def init_from_config(self, fish_num, region_num):
        return config.init_class(self, Region.config_section(fish_num, region_num))

    def config_section(fish_num, region_num):
        if isinstance(fish_num, str):
            return f"Fish {fish_num} Region {region_num}"
        else:
            return f"Fish {fish_num + 1} Region {region_num + 1}"

class Fish(UserDataClass):
    """
    Class that holds settings attached to a single fish. Includes notes on fish as well, list of 
    Region instances, and total number of images in acquisition of fish.

    ## Instance Attributes:

    #### self.not_config_props : list[str]
        list of instance attributes that should not be written to config

    #### region_list : list[Region]
        List of instances of Region

    #### fish_type : str
        type of fish being imaged (genotype, condition, etc)

    #### age : str
        fish age

    #### inoculum : str
        inoculum of fish

    #### add_notes : str
        any additional notes on fish

    #### num_images : int
        number of images to be acquired at this fish. set by update_num_images()

    ## Instance Methods

    #### remove_region(region_num)
        removes region from region_list at given region_num index

    #### append_blank_region()
        appends new instance of Region to region_list

    #### update_num_images()
        calculates number of images to be acquired and sets num_images attribute to said number
    """
    NOT_CONFIG_PROPS = ["not_config_props", "region_list"]

    fish_type: str = ""
    age: str = ""
    inoculum: str = ""
    add_notes: str = ""

    def __init__(self):
        self.region_list: list[Region] = []
        self.fish_type: str = Fish.fish_type
        self.age: str = Fish.age
        self.inoculum: str = Fish.inoculum
        self.add_notes: str = Fish.add_notes
        self.num_images: int = 0

    def update_region_list(self, region_num, region):
        try:
            self.region_list[region_num] = region
        except IndexError:
            self.region_list.append(region)

    def remove_region(self, region_num):
        del self.region_list[region_num]
    
    def append_blank_region(self) -> Region:
        region = Region()
        self.region_list.append(region)
        return region

    def update_num_images(self):
        fish_num_images = 0
        for region in self.region_list:
            region.update_num_images()
            fish_num_images += region.num_images
        self.num_images = fish_num_images

    def is_imaging_enabled(self):
        for region in self.region_list:
            if region.is_imaging_enabled():
                return True
        else:
            return False

    def write_to_config(self, fish_num):
        config.write_class(self, Fish.config_section(fish_num))

    def init_from_config(self, fish_num):
        return config.init_class(self, Fish.config_section(fish_num))

    def config_section(fish_num):
        if isinstance(fish_num, str):
            return f"Fish {fish_num} Notes"
        else:
            return f"Fish {fish_num + 1} Notes"


class AcquisitionSettings(UserDataClass):
    """
    Data class that stores properties that apply to the entire image acquisition. Also includes list that holds Fish
    instances, which are the main objects (along with Region instances) used during an image acquisition.

    ## Class Attributes:

    #### image_width : int
        width of image in pixels according to MM

    #### image_height : int
        height of image in pixels according to MM

    #### image_size_mb : float
        image size according to MM (sort of). Calculatiom I use is just width*height*(bit_depth)/10**6

    #### min_exposure : int
        minimum exposure of camera (for Hamamatsu, min is 1 ms and max is 10000 ms).

    #### max_exposure : int
        maximum exposure of camera.


    ## Instance Attributes:

    #### fish_list : list[Fish]
        list that holds instances of Fish.

    #### adv_settings : AdvancedSettings
        instance of AdvancedSettings

    #### total_num_images : int
        total number of images in acquisition.

    #### time_points_bool : bool
        if True, a time series based on num_time_points and time_points_interval will be enabled.

    #### num_time_points : int
        number of time points. Note that this is a property and that _num_time_points shouldnever be accessed directly.

    #### time_points_interval_min : int
        interval (in minutes) between time points in time series. If set to 0 (or if acquisition of a single time 
        point takes longer than the interval), acquisition of the next time point will start immediately.

    #### channel_order_list : list[str]
        channel order acquisition used during acquisition. If multiple channels are selectedfor a specific type of 
        image acquisition in a Region instance (video, snap, z-stack, etc.), the channels will be acquired in this 
        order.

    #### directory : str
        path where acquisition is to be saved.
    
    #### researcher : str
        name of researcher
    
    ## Instance Methods:

    #### remove_fish(fish_num)
        removes fish at given fish_num index.

    #### append_blank_fish()
        Appends new Fish() object to self.fish_list

    #### update_num_images()
        Calculates number of images to be acquired during acquisition and sets self.num_imagesto said number.

    """

    NOT_CONFIG_PROPS = ["fish_list", "adv_settings"]

    image_width: int = core.get_image_width()
    image_height: int = core.get_image_height()
    bytes_per_pixel: int = core.get_bytes_per_pixel()
    image_size_mb: float = (image_width * image_height * bytes_per_pixel)*globals.B_TO_MB

    def __init__(self):
        self.fish_list: list[Fish] = []
        self.adv_settings: AdvancedSettings = AdvancedSettings()
        self.total_num_images: int = 0
        self.images_per_time_point: int = 0
        self.time_points_enabled: bool = False
        self._num_time_points: int = 1
        self.time_points_interval_min: int = 0
        self.core_channel_list: list[str] = pycro.get_channel_list()
        self.channel_order_list: list[str] = deepcopy(self.core_channel_list)
        self.directory: str = "G:/"
        self.researcher: str = ""
        self.init_from_config()

    @property
    def num_time_points(self):
        return self._num_time_points
    
    @num_time_points.setter
    def num_time_points(self, value):
        if value < 1:
            self._num_time_points = 1
        else:
            self._num_time_points = value

    def is_imaging_enabled(self):
        for fish in self.fish_list():
            if fish.is_imaging_enabled():
                return True
        else:
            return False

    def remove_fish(self, fish_num: int):
        del self.fish_list[fish_num]

    def update_fish_list(self, fish_num: int, fish: Fish):
        try:
            self.fish_list[fish_num] = fish
        except IndexError:
            self.fish_list.append(fish)

    def append_blank_fish(self) -> Fish:
        fish = Fish()
        self.fish_list.append(fish)
        return fish

    def update_num_images(self):
        images_per_time_point = 0
        for fish in self.fish_list:
            fish.update_num_images()
            images_per_time_point += fish.num_images
        self.images_per_time_point = images_per_time_point
        if self.time_points_enabled:
            self.total_num_images = images_per_time_point*self.num_time_points
        else:
            self.total_num_images = images_per_time_point
    
    def update_image_size():
        width = core.get_image_width()
        height = core.get_image_height()
        bytes_per_pixel = core.get_bytes_per_pixel()
        AcquisitionSettings.image_width = width
        AcquisitionSettings.image_height = height
        AcquisitionSettings.bytes_per_pixel = bytes_per_pixel
        AcquisitionSettings.image_size_mb = width*height*bytes_per_pixel*globals.B_TO_MB

    def fix_channel_list_order(self):
        for fish in self.fish_list:
            for region in fish.region_list:
                self.arrange_list_from_order_list(region.snap_channel_list)
                self.arrange_list_from_order_list(region.z_stack_channel_list)
                self.arrange_list_from_order_list(region.video_channel_list)

    def arrange_list_from_order_list(self, lst: list):
        channel_num = 0
        for channel in self.channel_order_list:
            if channel in lst:
                cur_pos = lst.index(channel)
                lst[channel_num], lst[cur_pos] = lst[cur_pos], lst[channel_num]
                channel_num += 1

    def write_to_config(self):
        """
        Writes instance attributes to Config section of acquisition settings, advanced settings,
        and all intances of fish in fish_list to config.
        """
        config.write_class(self)
        config.write_class(self.adv_settings)
        self._write_fish_list_to_config()
    
    #write_to_config helper
    def _write_fish_list_to_config(self):
        self._remove_fish_sections()
        for fish_num, fish in enumerate(self.fish_list):
            fish.write_to_config(fish_num)
            for region_num, region in enumerate(fish.region_list):
                region.write_to_config(fish_num, region_num)

    def _remove_fish_sections(self):
        """
        Checks for all sections that match format of region_section and fish_section and removes them.
        Example: "Fish 1 Notes" is of the form f"Fish {'[0-9]'} Notes", as is "Fish 150 Notes",
        so bool(re.match()) returns True.
        """
        for section in config.sections():
            region_section_bool = bool(re.match(Region.config_section('[0-9]', '[0-9]'), section))
            fish_section_bool = bool(re.match(Fish.config_section('[0-9]'), section))
            if region_section_bool or fish_section_bool:
                config.remove_section(section)

    def init_from_config(self):
        """
        Initializes acq_settings instance attributes with values read from config section
        """
        config.init_class(self)
        self._init_channel_order_list()
        self._init_fish_list_from_config()

    #config init helpers
    def _init_channel_order_list(self):
        """
        FIrst, verifies that channel_order_list contains only channels in core_channel list.

        """
        if self._verify_channel_order_list():
            self._add_missing_channels_to_order_list()

    def _verify_channel_order_list(self):
        """
        If channel_order_list contains channel not in core_channel_list, sets channel_order_list to
        copy of core_channel_list and returns False. Else, returns True.
        """
        for channel in self.channel_order_list:
            if channel not in self.core_channel_list:
                self.channel_order_list = deepcopy(self.core_channel_list)
                return False
        return True

    def _add_missing_channels_to_order_list(self):
        """
        Appends all channels in core_channel_list but not in channel_order_list to channel_order_list.
        """
        for channel in self.core_channel_list:
            if channel not in self.channel_order_list:
                self.channel_order_list.append(channel)

    def _init_fish_list_from_config(self):
        fish_num = 0
        while True:
            fish = Fish()
            if fish.init_from_config(fish_num):
                self.fish_list.append(fish)
            else:
                break
            self._init_regions_from_config(fish, fish_num)
            fish_num += 1
    
    def _init_regions_from_config(self, fish: Fish, fish_num: int):
        region_num = 0
        while True:
            region = Region()
            if region.init_from_config(fish_num, region_num):
                fish.region_list.append(region)
            else:
                break
            region_num += 1 
            

class AdvancedSettings(UserDataClass):
    """
    Class that holds advanced settings for acquisition.

    General idea of this class is to hold properties that the average user shouldn't need to worry about and
    that are reset between application sessions.

    ## Instance Attributes:
    
    #### z_stack_spectral_bool : bool
        If True, z-stacks will be spectral. A spectral z-stack takes an image in every channel before moving to 
        the next z-position. It is MUCH slower than a normal z-stack and should only be used if you need to. 
        Please see the Acquisition class for more details.

    #### speed_list : list[float]
        list of stage speeds (in um/s) that are available to the user for z-stacks. 30 should be the default.

    #### z_stack_stage_speed : float
        currently set stage speed (in um/s) to be used during z-stack

    #### z_stack_exposure : float
        exposure time for z-stacks. Note that this is a property, so _z_stack_exposure should not be directly 
        accessed. Read property and setter attributes for more details.

    #### video_spectral_bool : bool
        If True, videos will be spectral. Same as spectral z_stack except stage does notmove between spectral 
        images.

    #### acq_order : AcquisitionOrder()
        Enum that determines the acquisition order. See the AcquisitionOrder valuesfor more details.

    #### edge_trigger_bool : bool
        If True, camera is set to edge trigger mode. If False, camera is set to sync readout. See below 
        z_stack_exposure property and setter and Hamamatsu documentation for more details.

    #### lsrm_bool : bool
        If True, lightsheet readout mode is enabled. See SPIMGalvo lsrm(), lsrm methods in HardwareCommands, 
        and Hamamatsu documentation for more details.

    #### backup_directory_enabled : bool
        If True, backup_directory is enabled for acquisition. Path set in backup_directory will replace the 
        directory set in AcquisitionSettings in acquisition if space at that directory gets low during acquisition.

    #### backup_directory : str
        Second save path to be changed to if directory in AcquisitionSettings gets low during an acquisition. 
        Will only be used if backup_directory_enabled is True.
    """

    def __init__(self):
        self.spectral_z_stack_enabled: bool = False
        self.speed_list: list[int] = [15, 30]
        self.z_stack_stage_speed: int = self.speed_list[1]
        self.z_stack_exposure: float = globals.z_stack_speed_to_exposure(self.z_stack_stage_speed)
        self.spectral_video_enabled: bool = False
        self.acq_order = AcquisitionOrder.TIME_SAMP
        self.edge_trigger_enabled: bool = False
        self.lsrm_enabled: bool = False
        self.backup_directory_enabled: bool = False
        self.backup_directory: str = 'F:/'
        self.enable_mid_acq_editing: bool = False
    
    @property
    def z_stack_exposure(self):
        return self._z_stack_exposure
    
    @z_stack_exposure.setter
    def z_stack_exposure(self, value):
        #Maximum exp when performing continuous z-stack is floor(1/z_stack_speed) due to how the triggering works. 
        #This makes it so that if continuous z-stack is enabled and an exp time greater than this vaolue is entered, 
        #it is corrected.
        if not self.spectral_z_stack_enabled:
            self._z_stack_exposure = int(min(np.floor(1/(self.z_stack_stage_speed*globals.UM_TO_MM)), value))
        else:
            self._z_stack_exposure = value

    def write_to_config(self):
        return super().write_to_config()

class AcquisitionOrder(Enum):
    """
    Enum class to select acquisition order.
    
    ## enums:

    #### SAMP_TIME
        sample is iterated in outermost loop. This causes a full time series to be performed at each sample before 
        moving to the next.

    #### TIME_SAMP
        time_point is iterated in the outermost loop. the default acquisition order. For each time point, 
        each sample is imaged in sequence before moving to the next time point.
    """

    SAMP_TIME = 1
    TIME_SAMP = 2
