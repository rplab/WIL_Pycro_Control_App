from utils import globals

class AcquisitionDirectory(object):
    """
    Class to create and update directory for acquisition. As the acquisition progresses, fish, region, acq_type,
    and time_point are updated. Finally in the imaging sequences, get_directory() is called to get the updated
    directory as a string to be passed to a datastore.
    """
    FOLDER_NAME = "Acquisition"
        
    def __init__(self, directory: str):
        self.root = globals.get_unique_directory(f"{directory}/{self.FOLDER_NAME}")
        self._fish = "fish1"
        self._region = "region1"
        self._acq_type = "acq_type"
        self._time_point = "timepoint1"

    def set_fish_num(self, fish_num):
        self._fish = f"fish{fish_num + 1}"

    def set_region_num(self, region_num):
        self._region = f"region{region_num + 1}"

    def set_acq_type(self, acq_type):
        self._acq_type = acq_type

    def set_time_point(self, time_point):
        self._time_point = f"timepoint{time_point + 1}"

    def change_root(self, new_root):
        self.root = globals.get_unique_directory(f"{new_root}/{self.FOLDER_NAME}")

    def get_file_name(self):
        return f"{self._fish}/{self._region}/{self._acq_type}/{self._time_point}".replace("/", "_")

    def get_directory(self):
        return f"{self.root}/{self._fish}/{self._region}/{self._acq_type}/{self._time_point}/{self.get_file_name()}"
    