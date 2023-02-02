"""
Sets up logger format. If logger is needed, should be created via "from logging import Logger",
and then Logger(name), where name is a string with the name of the class or module.
"""

import datetime
import logging
import os
import time

logs_path = f"{os.curdir}/logs"
log_file_name = f"{logs_path}/logs{time.time()}_{datetime.date.today()}.log"
if not os.path.isdir(logs_path):
    os.mkdir(logs_path)
log_format = "%(levelname)s - %(asctime)s [%(name)s] - %(message)s"
logging.basicConfig(filename=log_file_name, filemode="w", format=log_format, level=logging.DEBUG)
