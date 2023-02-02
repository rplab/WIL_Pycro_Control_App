import ast
import configparser
import logging
import os


class Config(configparser.ConfigParser):
    """
    Class that extends configparser. Used to write and read configuration file,
    which are then used to initialize values in class instances.

    Future Changes:

    - _config_section_read() only reads in attributes that are already part of the class.
    Could maybe add a way to dynamically add attributes to class. Only problem that it 
    currently determines the type by the type of the attribute initialized in the class,
    so would need to figure out type evaluating works.

    - get rid of this and use JSON instead
    """

    COMMENTS_SECTION = "COMMENTS"
    DEFAULT_FILE_NAME = "config.cfg"

    def __init__(self, file_path: str = None):
        super().__init__()
        self.file_path = file_path or f"{os.curdir}/{Config.DEFAULT_FILE_NAME}"
        self._logger = logging.getLogger(self.__class__.__name__)
        self.init_from_config_file()
        self._write_comments_section()
    
    def write_config_file(self, file_path: str = None):
        """
        Writes current sections in Config to file at given path. 
        """
        file_path = file_path or self.file_path
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, "w") as configfile:
            self.write(configfile)
    
    def init_from_config_file(self, file_path: str = None):
        """
        Initializes Config from file located at file_path. 
        """
        file_path = file_path or self.file_path
        if os.path.exists(file_path):
            self.read(file_path)
            logging.getLogger().info("Config file read")
    
    def write_class(self, class_instance, section: str = None):
        """
        Writes section to Config with instance attributes of class_instance.
        If section = None, section name is assumed to be the name taken from
        class_instance.__class__.__name__ (this is recommended).
        """
        section = section or class_instance.__class__.__name__
        if not self.has_section(section):
            self.add_section(section)
        #This just iterates through the names of the instance attributes in acq_settings
        for key in vars(class_instance).keys():
            #NOT_CONFIG_PROPS is a list that holds names of instance attributes that
            #shouldn't be written to config.
            if hasattr(class_instance, "NOT_CONFIG_PROPS"):
                if not key in class_instance.NOT_CONFIG_PROPS:
                    #adds a section with name and value of instance attribute
                    self.set(section, key, str(vars(class_instance)[key]))
            else:
                self.set(section, key, str(vars(class_instance)[key]))
        self.write_config_file(self.file_path)
    
    def init_class(self, class_instance, section: str = None):
        """
        Initializes instance attributes of class_instance from values in section, if it exists.
        If section = None, section name is assumed to be the name taken from class_instance.__class__.__name__ 
        (this is recommended for classes with only one instance). 
        
        If section exists in config, returns True. Else, returns False.
        """
        if not section:
            section = class_instance.__class__.__name__
        if has_section := self.has_section(section):
            self._read_config_section(class_instance, section)
            self.write_class(class_instance, section)
        return has_section

    def _read_config_section(self, class_instance, section: str):
        """
        Sets class_instance attributes to key-value pairs in section.

        Currently supports int, float, bool, str, and lists and dicts of these types.
        Could add more if it's necessary in the future.
        """
        key_list = [item[0] for item in self.items(section)]
        for key in vars(class_instance).keys():
            if key in key_list:
                try:
                    if type(vars(class_instance)[key]) == int:
                        vars(class_instance)[key] = self.getint(section, key)
                    elif type(vars(class_instance)[key]) == float:
                        vars(class_instance)[key] = self.getfloat(section, key)
                    elif type(vars(class_instance)[key]) == bool:
                        vars(class_instance)[key] = self.getboolean(section, key)
                    elif type(vars(class_instance)[key]) == str:
                        vars(class_instance)[key] = self.get(section, key)
                    elif type(vars(class_instance)[key]) == list:
                        vars(class_instance)[key] = ast.literal_eval(self.get(section, key))
                    elif type(vars(class_instance)[key]) == dict:
                        vars(class_instance)[key] = ast.literal_eval(self.get(section, key))
                except:
                    exception = f"{section} {key} invalid data type for config initialization"
                    self._logger.exception(exception)
                else:
                    info = f"{section} {key} read"
                    self._logger.info(info)

    def _write_comments_section(self):
        """
        Adds in comments section to config if it doesn't exist.
        """
        section = Config.COMMENTS_SECTION
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, "COMMENTS", "PLEASE DO NOT EDIT UNLESS YOU KNOW WHAT YOU ARE DOING")
        self.write_config_file(self.file_path)
