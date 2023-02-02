"""
This module holds the studio and core objects, which are used to access the Micro-Manager API. In addition,
it holds methods and classes that use the MM API.

Please see the following Micro-Manager 2.0 API guide:

https://micro-manager.org/Version_2.0_API

Core API:

https://micro-manager.org/apidoc/mmcorej/latest/mmcorej/CMMCore.html

Studio API:

https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/Studio.html

"""

import contextlib
from datetime import datetime
from pycromanager import Studio, Core, JavaObject
from utils import globals


studio = Studio()
core = Core()


_MULTIPAGE_TIFF = studio.data().get_preferred_save_mode().MULTIPAGE_TIFF
#These are found in the MM summary metadata class.
_C_AXIS = "channel"
_T_AXIS = "time"
_Z_AXIS = "z"
_P_AXIS= "position"


class image_coords_builder():
    """
    Essentially a Python copy of the coords builder in Micro-Manager (see DefaultCoordsBuilder). Contains 
    only the coords necessary to have same metadata format as MM Acquisitions (channel, z, time, and position).

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Coords.Builder.html

    ## Methods:

    every method returns self (akin the builder design), except for build() which returns an
    MM DefaultCoords object.

    #### c(channel_num:int)
        sets channel number

    #### z(z_num:int)
        sets z slice number

    #### t(time_num:int)
        sets time number

    #### build()
        returns MM DefaultCoords object
    """
    
    def __init__(self):
        self._coords_builder = JavaObject("org.micromanager.data.internal.DefaultCoords$Builder")

    def c(self, num_c):
        self._coords_builder.c(num_c)
        return self

    def z(self, num_z):
        self._coords_builder.z(num_z)
        return self
    
    def t(self, num_t):
        self._coords_builder.t(num_t)
        return self

    #p (position) is pretty much only added to be used in summary metadata. 
    def p(self, num_p):
        self._coords_builder.p(num_p)
        return self

    def build(self):
        return self._coords_builder.build()


class summary_metadata_builder():
    """
    Essentially a Python copy of the summary metadata builder in Micro-Manager (see DefaultSummaryMetadataBuilder). 
    Contains only the coords necessary to have acceptable metadata (channel, z, and time).

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/SummaryMetadata.Builder.html

    The axis order is determined on the order of the called methods. That is, if channel_list(), then z(), then t() 
    are called, then the axis order will be channel, z, time. The order in which these are added should be from 
    inner-most iterated to outer-most.

    As an example, for a normal video acquisition, the inner-most iterated is the time (frame number), the second
    is channel, and for a video that's all we have. Thus, the time (number of frames) should be set first and then 
    the channel list.

    ## Notes:
    - I've done my best to set these methods up in such a way that the metadata format is as similar as possible to
    the Multi-Dimensional Acquisition metadata, although there are still differences. Could use work in the future.

    ## Methods:

    every method returns self (akin the builder design), except for build() which returns an
    MM DefaultCoords object.

    #### channel_list(channel_list:list)
        adds channel_list as channel_names for summary metadata, sets intended number of channels
        to len(channel_list), and adds "channel" to axis order.

    #### z(z_num:int)
        adds "z" to axis order and sets intended number of z-slices to z_num

    #### t(t_num:int)
        adds "time" to axis order and sets intended number of time points to t_num

    #### step(step_size:int)
        sets step_size (currently only used in z-stack acquisitions)
        
    #### interval_ms(interval_ms:int)
        sets the time interval between images (currently only should be used in the standard video acquisition).

    #### build()
        returns MM DefaultSummaryMetadata object
    """
    def __init__(self):
        #unfortunately, can't just use a python list as axis_order() takes a java iterable object. Easiest
        #one to grab and use is ArrayList.
        self._axis_order = JavaObject("java.util.ArrayList")
        #default 1 is set for each coord so that the axes appear in the metadata. If nothing or 0 are set for an axis 
        #and coords is built, it won't appear.
        self._intended_builder = image_coords_builder().c(1).z(1).t(1).p(1)
        self._summary_builder = JavaObject("org.micromanager.data.internal.DefaultSummaryMetadata$Builder")
    
    def channel_list(self, channels):
        self._axis_order.add(_C_AXIS)
        
        channel_array = JavaObject("java.util.ArrayList")
        if isinstance(channels, list):
            self._intended_builder.c(len(channels))
            for channel in channels:
                channel_array.add(channel)
        else:
            self._intended_builder.c(1)
            channel_array.add(channels)

        self._summary_builder.channel_names(channel_array)
        return self

    def z(self, num_z):
        self._axis_order.add(_Z_AXIS)
        self._intended_builder.z(num_z)
        return self

    def t(self, num_t):
        self._axis_order.add(_T_AXIS)
        self._intended_builder.t(num_t)
        return self

    def p(self, num_p):
        self._axis_order.add(_P_AXIS)
        self._intended_builder.p(num_p)
        return self

    def step(self, step_size):
        self._summary_builder.z_step_um(step_size)
        return self
    
    def interval_ms(self, interval_ms):
        self._summary_builder.wait_interval(interval_ms)
        return self

    def _start_date(self):
        self._summary_builder.start_date(str(datetime.now()))
        return self

    def _finalize_axis_order(self):
        #Default order is cztp, so added in this order if not already added
        for axis in (_C_AXIS, _Z_AXIS, _T_AXIS, _P_AXIS):
            if not self._axis_order.contains(axis):
                self._axis_order.add(axis)

    def build(self):
        self._finalize_axis_order()
        self._start_date()
        self._summary_builder.axis_order(self._axis_order)
        self._summary_builder.intended_dimensions(self._intended_builder.build())
        return self._summary_builder.build()


class image_metadata_builder():
    """
    Essentially a Python copy of the image metadata builder in Micro-Manager (see DefaultImageMetadataBuilder). 
    Contains only the coords necessary to have acceptable metadata (x_pos, y_pos, z_pos). Most of the metadata
    (time image was received, camera used, pixel size, etc.) are set automatically by Micro-Manager.

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Metadata.Builder.html

    ## Methods:

    every method returns self (akin the builder design), except for build() which returns an
    MM DefaultCoords object.

    #### x(x_pos:int)
        adds x_pos as x_position to image metadata

    #### y(y_pos:int)
        adds y_pos as y_position to image metadata

    #### z(z_pos:int)
        adds z_pos as z_position to image metadata

    #### build()
        returns MM DefaultImageMetadata object
    """

    def __init__(self, image):
        self._meta_builder = image.get_metadata().copy_builder_preserving_uuid()

    def x(self, x_pos):
        self._meta_builder.x_position_um(x_pos)
        return self

    def y(self, y_pos):
        self._meta_builder.y_position_um(y_pos)
        return self

    def z(self, z_pos):
        self._meta_builder.z_position_um(z_pos)
        return self
    
    def build(self):
        return self._meta_builder.build()


def create_image_metadata(x_pos, y_pos, z_pos):
    """
    Alternative way of creating image metadata object.
    """
    return image_metadata_builder().x(x_pos).y(y_pos).z(z_pos).build()


class multipage_datastore():
    """
    Class that holds an MM multipage_tiff_datastore object. Methods are the same as MM counterparts
    except close() which supresses exceptions (mostly to avoid NullPointerException, which is thrown
    when the datastore is closed when it has no images).

    See: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Datastore.html
    """
    def __init__(self, save_path):
        save_path = globals.get_unique_directory(save_path)
        self._datastore = studio.data().create_multipage_tiff_datastore(save_path, True, False)
    
    def freeze(self):
        self._datastore.freeze()
    
    def put_image(self, image):
        self._datastore.put_image(image)
    
    def save(self):
        self.freeze()
        self._datastore.save()
    
    def set_summary_metadata(self, summary_metadata):
        self._datastore.set_summary_metadata(summary_metadata)
    
    def close(self):
        #If datastore has no images, throws a java NullPointerException. This supresses
        #that exception.
        with contextlib.suppress(Exception):
            self._datastore.close()


class ram_datastore():
    """
    Class that holds an MM ram_datastore object. Methods are the same as MM counterparts
    except close() which supresses exceptions (mostly to avoid NullPointerException, which is thrown
    when the datastore is closed when it has no images).

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Datastore.html
    """
    def __init__(self):
        self._datastore = studio.data().create_ram_datastore()
    
    def freeze(self):
        self._datastore.freeze()
    
    def put_image(self, image):
        self._datastore.put_image(image)
    
    def save(self, directory):
        #MM documentation says to "freeze" datastore after data is no longer being added.
        #Not sure if it actually makes a difference...
        self.freeze()
        self._datastore.save(_MULTIPAGE_TIFF, globals.get_unique_directory(directory))

    def set_summary_metadata(self, summary_metadata):
        self._datastore.set_summary_metadata(summary_metadata)
    
    def close(self):
        with contextlib.suppress(Exception):
            self._datastore.close()


def get_channel_list():
    """
    Returns a list of all presets in the group specified by channel_group_name.
    """
    core_channel_vector = core.get_available_configs(core.get_channel_group())
    return [core_channel_vector.get(i) for i in range(core_channel_vector.size())]


def pop_next_image():
    """
    grabs next image in image buffer and returns it as an MM image object
    
    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Image.html
    """
    tagged = core.pop_next_tagged_image()
    return studio.data().convert_tagged_image(tagged)
