import time
import numpy as np
import logging
from abc import ABC, abstractmethod
from copy import deepcopy
from acquisition import imaging_sequences
from hardware import stage
from models.acquisition.acquisition_user_data import AcquisitionSettings, Fish, Region
from models.acquisition.acquisition_directory import AcquisitionDirectory
from utils import exceptions, globals
from views import AcquisitionDialog

class AbstractAcquisitionSequence(ABC):
    # Reason for this is that disks write slower when they're full, which will cause timing
    # issues between timepoints.
    PERCENT_DISK_LIMIT = 0.8
    # If image sequence fails, reattempts this many times.
    ATTEMPT_LIMIT = 2
    # delay is pretty arbitrary. At the very least should be less than a second
    # to avoid inconsistency between timepoints.
    TIME_UPDATE_DELAY_S = .01

    @abstractmethod
    def run_acquisition(self):
        """
        starts acquisition.
        """
        pass

    def __init__(self, acq_settings: AcquisitionSettings, acq_dialog: AcquisitionDialog,
                 abort_flag: exceptions.AbortFlag, acq_directory: AcquisitionDirectory):
        self._logger = logging.getLogger(self._get_name())

        if acq_settings.adv_settings.enable_mid_acq_editing:
            self._acq_settings = acq_settings
        else:
            self._acq_settings = deepcopy(acq_settings)
        self._adv_settings = self._acq_settings.adv_settings
        self._acq_dialog = acq_dialog
        self._abort_flag = abort_flag
        self._acq_directory = acq_directory

    def _get_name(self):
        return self.__class__.__name__

    # time point helpers
    def _is_time_point_left(self, time_point):
        time_points_left = self._acq_settings.num_time_points - time_point
        return time_points_left > 1

    def _wait_for_next_time_point(self, start_time):
        while self._time_remaining(start_time) > 0:
            self._abort_check()
            self._time_left_dialog_update(start_time)
            time.sleep(self.TIME_UPDATE_DELAY_S)

    def _time_remaining(self, start_time):
        return self._acq_settings.time_points_interval_min*globals.MIN_TO_S - self._time_since_start(start_time)

    def _time_since_start(self, start_time):
        return time.time() - start_time

    def _acquire_fish_regions(self, fish: Fish):
        for region_num, region in enumerate(fish.region_list):
            self._abort_check()
            if region.is_imaging_enabled():
                self._region_num_update(region_num)

                self._move_to_region(region)
                self._run_imaging_sequences(region)

    def _run_imaging_sequences(self, region: Region):
        self._abort_check()
        if region.snap_enabled:
            self._status_update("Initializing Snap")
            self._acquire_snap(region)

        self._abort_check()
        if region.video_enabled:
            self._status_update("Initializing Video")
            if self._adv_settings.spectral_video_enabled:
                self._acquire_spectral_video(region)
            else:
                self._acquire_video(region)

        self._abort_check()
        if region.z_stack_enabled:
            self._status_update("Initializing Z Stack")
            if self._adv_settings.spectral_z_stack_enabled:
                self._acquire_spectral_z_stack(region)
            else:
                self._acquire_z_stack(region)

    def _acquire_snap(self, region: Region):
        # This update message pattern works with the use of the "yield" keyword. See acquisition_scripts
        # for more details.
        snap = imaging_sequences.Snap(region, self._acq_settings, self._abort_flag, self._acq_directory)
        for update_message in snap.run():
            self._status_update(update_message)

    def _acquire_video(self, region: Region):
        for attempt_num in range(self.ATTEMPT_LIMIT):
            try:
                video = imaging_sequences.Video(region, self._acq_settings, self._abort_flag, self._acq_directory)
                for update_message in video.run():
                    self._status_update(update_message)
            except exceptions.CameraTimeoutException:
                self._camera_timeout_dialog_update(attempt_num, "Video")
            else:
                break

    def _acquire_spectral_video(self, region: Region):
        spectral_video = imaging_sequences.SpectralVideo(region, self._acq_settings, self._abort_flag, self._acq_directory)
        for update_message in spectral_video.run():
            self._status_update(update_message)

    def _acquire_z_stack(self, region: Region):
        for attempt_num in range(self.ATTEMPT_LIMIT):
            try:
                z_stack = imaging_sequences.ZStack(region, self._acq_settings, self._abort_flag, self._acq_directory)
                for update_message in z_stack.run():
                    self._status_update(update_message)
            except exceptions.CameraTimeoutException:
                self._camera_timeout_dialog_update(attempt_num, "Z Stack")
            else:
                break

    def _acquire_spectral_z_stack(self, region: Region):
        spectral_z_stack = imaging_sequences.SpectralZStack(region, self._acq_settings, self._abort_flag, self._acq_directory)
        for update_message in spectral_z_stack.run():
            self._status_update(update_message)

    def _move_to_region(self, region: Region):
        self._abort_check()
        self._status_update("Moving to region")
        if region.z_stack_enabled and not (region.snap_enabled or region.video_enabled):
            stage.move_stage(region.x_pos, region.y_pos, region.z_stack_start_pos)
        else:
            stage.move_stage(region.x_pos, region.y_pos, region.z_pos)

    def _get_start_region(self, start_fish_num):
        for fish in self._acq_settings.fish_list[start_fish_num:]:
            if fish.is_imaging_enabled():
                for region in fish.region_list:
                    if region.is_imaging_enabled():
                        return region, self._acq_settings.fish_list.index(fish)
        else:
            return None, None

    # directory methods
    def _update_directory(self, fish: Fish):
        if not (self._second_path_in_root() or self._is_enough_space(fish)):
            self._acq_directory.change_root(self._adv_settings.backup_directory)

    def _second_path_in_root(self):
        return self._adv_settings.backup_directory in self._acq_directory.root

    def _is_enough_space(self, fish: Fish):
        return globals.is_enough_space(self._get_size_mb_of_fish(fish), self.PERCENT_DISK_LIMIT, self._acq_directory.root)

    def _get_size_mb_of_fish(self, fish: Fish):
        return fish.num_images*self._acq_settings.image_size_mb

    # acq_dialog methods
    def _set_region_label_num(self, region_num):
        self._acq_dialog.region_label.setText(f"Region {region_num + 1}")

    def _set_fish_label_num(self, fish_num: int):
        self._acq_dialog.fish_label.setText(f"Fish {fish_num + 1}")

    def _set_time_point_label_num(self, time_point: int):
        self._acq_dialog.time_point_label.setText(f"Time Point {time_point + 1}")

    def _camera_timeout_dialog_update(self, attempt_num: int, acq_type: str):
        message = f"{acq_type} failed. "
        if attempt_num < self.ATTEMPT_LIMIT - 1:
            message += f"reattempting {acq_type}."
        else:
            message += "skipping."

        self._status_update(message)

    def _time_left_dialog_update(self, start_time):
        minutes_left, remaining_seconds = self._get_minutes_and_seconds_left(start_time)

        update_message = "next time point:"
        if minutes_left:
            update_message = f"{update_message} {minutes_left} minutes"
        update_message = f"{update_message} {remaining_seconds} seconds"

        self._acq_dialog.acquisition_label.setText(update_message)

    def _get_minutes_and_seconds_left(self, start_time):
        total_seconds_left = int(np.ceil(self._time_remaining(start_time)))
        return divmod(total_seconds_left, globals.S_IN_MIN)

    def _status_update(self, message):
        """
        Displays message on acquisition label and writes it to logs
        """
        self._acq_dialog.acquisition_label.setText(message)
        self._logger.info(message)

    #general helpers
    def _region_num_update(self, region_num):
        self._acq_directory.set_region_num(region_num)
        self._set_region_label_num(region_num)
        self._status_update(f"Acquiring region {region_num + 1}")
    
    def _fish_num_update(self, fish_num):
        self._acq_directory.set_fish_num(fish_num)
        self._set_fish_label_num(fish_num)
        self._status_update(f"Acquiring fish {fish_num + 1}")

    def _time_point_num_update(self, time_point_num):
        self._acq_directory.set_time_point(time_point_num)
        self._set_time_point_label_num(time_point_num)
        self._status_update(f"Acquiring timepoint {time_point_num + 1}")

    def _abort_check(self):
        if self._abort_flag.abort:
            raise exceptions.AbortAcquisitionException