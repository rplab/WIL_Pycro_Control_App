from controllers import main_controller
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
   app = QApplication(sys.argv)
   controller = main_controller.MainController()
   app.exec_()
