# SVG to HDMI output test

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt5.QtSvg import QSvgWidget
from layout_colorwidget import Color
import config

class MainWindow(QMainWindow): # Main GUI for controlling photolithography settings and image
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGEN Photolithography Settings")


class LithoWindow(QMainWindow): # Create the window that the DLP will receieve
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image")

        # Attempt to move image to second display
        try:
            screen_geometry = QApplication.screens()[1].geometry()
            self.setGeometry(screen_geometry)
            self.showFullScreen()
            if screen_geometry.width() < config.LITHO_SIZE_PX_X or screen_geometry.height() < config.LITHO_SIZE_PX_Y:
                print("Warning: Second display resolution is smaller than lithography image size.")
                print("Image cropped to:")
                # Set to a square ratio based on max screen height
                config.LITHO_SIZE_PX_Y = screen_geometry.height()
                config.LITHO_SIZE_PX_X = screen_geometry.height()
                print(f"\tWidth: {config.LITHO_SIZE_PX_X} px")
                print(f"\tHeight: {config.LITHO_SIZE_PX_Y} px")

        except IndexError:
            screen_geometry = QApplication.screens()[0].geometry()
            print("Only one display detected; showing image on primary display.")
        except Exception as e:
            print(e)

        # Layout the SVG image smack in the center of the screen
        self.layout = QGridLayout()
        self.svg = QSvgWidget("svg_images\\25 EGen Logo.svg")
        self.layout.addWidget(self.svg, 0, 0)
        self.svg.setFixedSize(config.LITHO_SIZE_PX_X, config.LITHO_SIZE_PX_Y)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        

app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.show()

lithoWindow = LithoWindow()
lithoWindow.show()

app.exec()