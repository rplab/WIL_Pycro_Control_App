"""
This file contains all the controller classes. There are currrently three: One to control all
other controllers, one to control image acquisitions, and one more to control the galvo mirrors.
Each controller has essentially one associated view (although the acquisition controller has multiple
windows).

Notes for future developers:

If there's one thing I want future developers to get out of this design, it's modularity. I hope it's obvious
that designing additional controllers, completely separate from the image acquisition package that I've made,
is the intended development route. 

I've spent an incredible amount of time on documentation and readability for two reasons:

1. It looks nice :)

2. I have no idea what the programming background of the next person to develop this will be. 

When I started this job, my coding background was not great and the code that was left behind was incomprehensible 
(both because I was inexperienced and because it was awful). I wanted to make something that (hopefully) someone with 
just a bit of knowledge of microscope automation and object-oriented programming could figure out. 

Future Changes:
- I've done almost no formatting. Probably should format everything to be in accordance with PEP 8. Currently using 
120 line length limit, which I think is reasonable. 80 seems like way too little.

- All the controllers are so boilerplatey. Not sure if there's an elegant way around this just due to how the PyQt5
API is. Will thing more about this.
"""

import controllers.acquisition_controller
import views
from PyQt5 import QtCore

class MainController(object):
    def __init__(self):
        #Same instances of studio, core, mm_hardware_commands, and spim_commands used throughout
        self._main_window = views.MainWindow()
        self._acquisition_controller = controllers.acquisition_controller.AcquisitionController()
        
        #initialize main window and event handlers.
        self._main_window.cls_button.clicked.connect(self._cls_button_clicked)
        self._main_window.exit_button.clicked.connect(self._exit_button_clicked)

        #This flag is set to disable thebuttons on the top right of the window.
        self._main_window.setWindowFlags(QtCore.Qt.WindowTitleHint)
        
        self._main_window.show()

    def _cls_button_clicked(self):
        self._acquisition_controller.regions_dialog.show()
        self._acquisition_controller.regions_dialog.activateWindow()

    def _exit_button_clicked(self):
        quit()
        