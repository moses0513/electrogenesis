# SVG to HDMI output test

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSlider,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QSizePolicy
)
from PyQt5.QtSvg import QSvgWidget
from layout_colorwidget import Color
import config

class MainWindow(QMainWindow): # Main GUI for controlling photolithography settings and image
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGEN Photolithography Settings")

        # GUI is layed out as follows:
        # Two halves, left and right
        # Left half: Photolithography settings, Aligment assist settings
        # Right half: Photolithography preview, Toggle circle color selectors
        self.layout_top = QHBoxLayout()
        self.layout_L = QVBoxLayout()
        self.layout_R = QVBoxLayout()
        self.layout_exposure = QHBoxLayout()
        self.layout_circle = QHBoxLayout()

        # LEFT HALF
        # Photolithography settings (outputs to UV LEDs)
        self.photo_text_title = QLabel("Photolithography Settings")
        self.photo_text_file = QLabel(f'Image File: {config.PHOTO_FILE}')
        self.photo_cbox = QComboBox()
        self.photo_cbox.addItems(os.listdir("svg_images"))
        self.photo_cbox.setCurrentIndex(0)

        self.photo_text_UV = QLabel("UV LED Brightness:")
        self.photo_slider_UV = QSlider()
        self.photo_slider_UV.setOrientation(1)
        self.photo_slider_UV.setMinimum(0)
        self.photo_slider_UV.setMaximum(255)
        self.photo_slider_UV.setValue(0)

        # Alignment layer settings (can output to Red or Green LEDs)
        self.assist_text_title = QLabel("Alignment Assist:")
        self.assist_text_file = QLabel(f'Image File: {config.PHOTO_FILE}')
        self.assist_cbox = QComboBox()
        self.assist_cbox.addItems(os.listdir("svg_images"))
        self.assist_cbox.setCurrentIndex(0)

        # Red and Green LED brightness sliders
        self.assist_text_RED = QLabel("Red LED Brightness:")
        self.assist_slider_RED = QSlider()
        self.assist_slider_RED.setOrientation(1)
        self.assist_slider_RED.setMinimum(0)
        self.assist_slider_RED.setMaximum(255)
        self.assist_slider_RED.setValue(0)

        self.assist_text_GREEN = QLabel("Green LED Brightness:")
        self.assist_slider_GREEN = QSlider()
        self.assist_slider_GREEN.setOrientation(1)
        self.assist_slider_GREEN.setMinimum(0)
        self.assist_slider_GREEN.setMaximum(255)
        self.assist_slider_GREEN.setValue(0)

        # Add widgets to left layout
        self.layout_L.addWidget(self.photo_text_title)
        self.layout_L.addWidget(self.photo_text_file)
        self.layout_L.addWidget(self.photo_cbox)
        self.layout_L.addWidget(self.photo_text_UV)
        self.layout_L.addWidget(self.photo_slider_UV)
        self.layout_L.addWidget(self.assist_text_title)
        self.layout_L.addWidget(self.assist_text_file)
        self.layout_L.addWidget(self.assist_cbox)
        self.layout_L.addWidget(self.assist_text_RED)
        self.layout_L.addWidget(self.assist_slider_RED)
        self.layout_L.addWidget(self.assist_text_GREEN)
        self.layout_L.addWidget(self.assist_slider_GREEN)

        # RIGHT HALF
        # Photolithography preview
        self.preview_text_title = QLabel("Photolithography Preview:")
        self.preview_svg = QSvgWidget(config.PHOTO_FILE)
        self.preview_svg.setFixedSize(config.LITHO_SIZE_PX_X//4, config.LITHO_SIZE_PX_Y//4)
        
        # Exposure time
        self.exposure_label = QLabel("Exposure Time:")

        # Exposure time spinbox
        self.exposure_spinbox = QSpinBox()
        self.exposure_spinbox.setMinimum(0)
        self.exposure_spinbox.setMaximum(30)
        self.exposure_spinbox.setValue(15)
        self.exposure_spinbox.suffix = " sec"

        # Exposure start/stop buttons
        self.exposure_STOP = QPushButton("STOP")
        self.exposure_STOP.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exposure_START = QPushButton("START")
        self.exposure_START.setStyleSheet("background-color: green; color: white; font-weight: bold;")

        # Add widgets to right layout
        self.layout_R.addLayout(self.layout_circle)
        self.layout_R.addWidget(self.preview_text_title)
        self.layout_R.addWidget(self.preview_svg)
        self.layout_exposure.addWidget(self.exposure_label)
        self.layout_exposure.addWidget(self.exposure_spinbox)
        self.layout_exposure.addWidget(self.exposure_STOP)
        self.layout_exposure.addWidget(self.exposure_START)
        self.layout_R.addLayout(self.layout_exposure)


        self.layout_top.addLayout(self.layout_L)
        self.layout_top.addLayout(self.layout_R)
        # self.layout_top.insertSpacerItem(1, QSizePolicy.Expanding)

        self.widget = QWidget()
        self.widget.setLayout(self.layout_top)
        self.setCentralWidget(self.widget)


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
        # self.layout = QGridLayout()
        self.svg = QSvgWidget("svg_images\\25 EGen Logo.svg")
        # self.layout.addWidget(self.svg, 0, 0)
        self.svg.setFixedSize(config.LITHO_SIZE_PX_X, config.LITHO_SIZE_PX_Y)

        # self.widget = QWidget()
        # self.widget.setLayout(self.layout)
        self.setCentralWidget(self.svg)
        

app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.show()

# lithoWindow = LithoWindow()
# lithoWindow.show()

app.exec()