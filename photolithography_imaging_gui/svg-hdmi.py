# SVG to HDMI output test

"""
TO-DO:

_ Change SVG code to PNG code
X Make SVGs update when new photo/assist files are selected from GUI
X Make second window reflect preview window
X Fix broken preview (happened right after adding DLP_preview_view to second display)
X Prevent scrolling on second window
X Dialog box to confirm start or cancel
_ Update aligment assist layers on second monitor 
_ Add circle asset with adjustable dia, x-offset and y-offset
_ Color filtering
_ [Optional] Runtime dialog with stopwatch, goal
_ Lock aspect ratio of photolithography preview

"""

import sys, os
import config
import image_processing
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QGraphicsScene,
    QGraphicsColorizeEffect,
    QGraphicsView,
    QVBoxLayout, 
    QHBoxLayout,
    QStackedLayout,
    QLabel,
    QComboBox,
    QSlider,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QSpacerItem,
    QMessageBox,
    QSizePolicy
)
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QResizeEvent, QBrush, QColor

images = os.listdir("svg_images")
screens = QApplication.screens()

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        # Fixed aspect ratio for the viewport
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy = sizePolicy

        noScroll = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(noScroll)
        self.setHorizontalScrollBarPolicy(noScroll)
        
        
    def sizeHint(self):
        return QSize(400, 600)
        # return QSize(int(DLP.width//2.5), int(DLP.height//2.5))
    def heightForWidth(self, width):
        return width * 1.5
    def resizeEvent(self, event: QResizeEvent):
        super(GraphicsView, self).resizeEvent(event)
        self.windowRect = QRectF(0, 0, DLP.width, DLP.height)
        self.fitInView(self.windowRect, Qt.KeepAspectRatio)

    

class MainWindow(QMainWindow): # Main GUI for controlling photolithography settings and image
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGEN Photolithography Settings")
        
        # Style and positioning
        QApplication.setStyle("Fusion") 
        try:
            with open("style.css", "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            print("You're out of style :(")
            print(e)

        # GUI is layed out as follows:
        # Two halves, left and right
        # Left half: Photolithography settings, Aligment assist settings
        # Right half: Photolithography preview, Toggle circle color selectors
        self.layout_top = QHBoxLayout()
        self.layout_L = QVBoxLayout()
        self.layout_R = QVBoxLayout()
        self.layout_exposure = QHBoxLayout()
        self.layout_circle = QHBoxLayout()
        self.layout_circle_dia = QVBoxLayout()
        self.layout_circle_offset_x = QVBoxLayout()
        self.layout_circle_offset_y = QVBoxLayout()
        self.layout_svg_preview = QStackedLayout()

        # LEFT HALF
        # Photolithography settings (outputs to UV LEDs)
        self.photo_text_title = QLabel("Photolithography Settings")
        QLabel.setAlignment(self.photo_text_title, Qt.AlignCenter)

        self.photo_text_file = QLabel(f'Image File: {config.PHOTO_FILE}')
        self.photo_cbox = QComboBox()
        self.photo_cbox.addItems(images)
        try:
            # By default, select the file in config.py
            self.photo_cbox.setCurrentIndex(images.index("25 EGen Logo.svg"))
        except:
            self.photo_cbox.setCurrentIndex(0)

        self.photo_text_UV = QLabel(f'UV LED Brightness: {config.DEFAULT_BRIGHTNESS_UV}')
        self.photo_slider_UV = QSlider()
        self.photo_slider_UV.setOrientation(1)
        self.photo_slider_UV.setMinimum(0)
        self.photo_slider_UV.setMaximum(255)
        self.photo_slider_UV.setValue(config.DEFAULT_BRIGHTNESS_UV)

        # Alignment layer settings (can output to Red or Green LEDs)
        self.assist_text_title = QLabel("Alignment Assist:")
        self.assist_text_file = QLabel(f'Image File: {config.PHOTO_FILE}')
        self.assist_cbox = QComboBox()
        self.assist_cbox.addItems(images)
        try:
            # By default, select the file in config.py
            self.assist_cbox.setCurrentIndex(images.index("25 EGen Logo.svg"))
        except:
            self.assist_cbox.setCurrentIndex(0)

        # Red and Green LED brightness sliders
        self.assist_text_RED = QLabel(f'Red LED Brightness: {config.DEFAULT_BRIGHTNESS_RED}')
        self.assist_slider_RED = QSlider()
        self.assist_slider_RED.setOrientation(1)
        self.assist_slider_RED.setMinimum(0)
        self.assist_slider_RED.setMaximum(255)
        self.assist_slider_RED.setValue(config.DEFAULT_BRIGHTNESS_RED)

        self.assist_text_GREEN = QLabel(f'Green LED Brightness: {config.DEFAULT_BRIGHTNESS_GREEN}')
        self.assist_slider_GREEN = QSlider()
        self.assist_slider_GREEN.setOrientation(1)
        self.assist_slider_GREEN.setMinimum(0)
        self.assist_slider_GREEN.setMaximum(255)
        self.assist_slider_GREEN.setValue(config.DEFAULT_BRIGHTNESS_GREEN)

        self.spacer = QSpacerItem(40, 40)

        # Add widgets to left layout
        self.layout_L.addWidget(self.photo_text_title)
        self.layout_L.addSpacerItem(self.spacer)
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
        self.layout_L.addSpacerItem(self.spacer)

        # RIGHT HALF
        # Photolithography preview
        # Make a miniature scene that replicates the DLP output
        self.preview_text_title = QLabel("Photolithography Preview:")
        QLabel.setAlignment(self.preview_text_title, Qt.AlignCenter)

        self.DLP_preview_scene = QGraphicsScene()
        self.DLP_preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0))) # Complete blackout background
        
        self.photo_svg = QGraphicsSvgItem(config.PHOTO_FILE)
        self.align_svg = QGraphicsSvgItem(config.ALIGNMENT_FILE)
        # self.DLP_preview_scene.addItem(self.photo_svg)
        # self.DLP_preview_scene.addItem(self.align_svg)
        self.recolored_blend = image_processing.add_images(self.photo_svg, self.align_svg)
        self.DLP_preview_scene.addItem(self.recolored_blend)
        self.photo_svg.setZValue(2)
        self.align_svg.setZValue(1)
        self.DLP_preview_view = GraphicsView(self.DLP_preview_scene, self)

        

        # Output resolution:
        self.resolution_label = QLabel(f"Output resolution: {DLP.width} x {DLP.height}")        
        
        # Exposure time
        self.exposure_label = QLabel("Exposure Time:")

        # Exposure time spinbox
        self.exposure_spinbox = QDoubleSpinBox()
        self.exposure_spinbox.setRange(0, 30)
        self.exposure_spinbox.setValue(config.DEFAULT_EXPOSURE_TIME)
        self.exposure_spinbox.suffix = " sec"
        self.exposure_spinbox.setDecimals(2)

        # Exposure start/stop buttons
        self.exposure_STOP = QPushButton("STOP")
        self.exposure_STOP.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exposure_START = QPushButton("START")
        self.exposure_START.setStyleSheet("background-color: green; color: white; font-weight: bold;")

        # Alignment SVG layer
        self.alignment_svg_checkbox = QCheckBox("Draw alignment SVG on wafer")

        # Alignment circle layer
        self.alignment_circle_checkbox = QCheckBox("Draw alignment circle on wafer")
        self.alignment_circle_text = QLabel("Aligment circle settings:")

        self.alignment_circle_spinbox_dia_label = QLabel("Diameter (px):")
        self.alignment_circle_spinbox_dia = QSpinBox()
        self.alignment_circle_spinbox_dia.setRange(10, 2000)
        self.layout_circle_dia.addWidget(self.alignment_circle_spinbox_dia_label)
        self.layout_circle_dia.addWidget(self.alignment_circle_spinbox_dia)

        self.alignment_circle_spinbox_offset_x_label = QLabel("Offset X (px):")
        self.alignment_circle_spinbox_offset_x = QSpinBox()
        self.alignment_circle_spinbox_offset_x.setRange(-1000, 1000)
        self.layout_circle_offset_x.addWidget(self.alignment_circle_spinbox_offset_x_label)
        self.layout_circle_offset_x.addWidget(self.alignment_circle_spinbox_offset_x)

        self.alignment_circle_spinbox_offset_y_label = QLabel("Offset Y (px):")
        self.alignment_circle_spinbox_offset_y = QSpinBox()
        self.alignment_circle_spinbox_offset_y.setRange(-1000, 1000)
        self.layout_circle_offset_y.addWidget(self.alignment_circle_spinbox_offset_y_label)
        self.layout_circle_offset_y.addWidget(self.alignment_circle_spinbox_offset_y)

        self.layout_circle.addLayout(self.layout_circle_dia)
        self.layout_circle.addLayout(self.layout_circle_offset_x)
        self.layout_circle.addLayout(self.layout_circle_offset_y)
        

        # Add widgets to right layout
        self.layout_R.addWidget(self.preview_text_title)
        # self.layout_svg_preview.addWidget(self.preview_svg_outline)
        # self.layout_svg_preview.addWidget(self.preview_svg)
        # self.layout_svg_preview.setCurrentWidget(self.preview_svg)
        # self.layout_R.addLayout(self.layout_svg_preview)
        self.layout_R.addWidget(self.DLP_preview_view)
        self.layout_R.addWidget(self.resolution_label)
        self.layout_exposure.addWidget(self.exposure_label)
        self.layout_exposure.addWidget(self.exposure_spinbox)
        self.layout_exposure.addWidget(self.exposure_STOP)
        self.layout_exposure.addWidget(self.exposure_START)
        self.layout_R.addLayout(self.layout_exposure)
        self.layout_R.addWidget(self.alignment_svg_checkbox)
        self.layout_R.addWidget(self.alignment_circle_checkbox)
        self.layout_R.addWidget(self.alignment_circle_text)
        self.layout_R.addLayout(self.layout_circle)

        self.layout_top.addLayout(self.layout_L)
        self.layout_top.addLayout(self.layout_R)
        # self.layout_top.insertSpacerItem(1, QSizePolicy.Expanding)

        self.widget = QWidget()
        self.widget.setLayout(self.layout_top)
        self.setCentralWidget(self.widget)

        ############## Button Bindings ##############
        # Combo boxes
        self.photo_cbox.currentIndexChanged.connect(lambda: self.update_svg_file("PHOTO"))
        self.assist_cbox.currentIndexChanged.connect(lambda: self.update_svg_file("ALIGN"))
        # Sliders
        self.photo_slider_UV.valueChanged.connect(lambda: self.photo_text_UV.setText(f'UV LED Brightness: {self.photo_slider_UV.value()}'))
        self.assist_slider_RED.valueChanged.connect(lambda: self.assist_text_RED.setText(f'Red LED Brightness: {self.assist_slider_RED.value()}'))
        self.assist_slider_GREEN.valueChanged.connect(lambda: self.assist_text_GREEN.setText(f'Green LED Brightness: {self.assist_slider_GREEN.value()}'))
        # Start/stop buttons
        self.exposure_START.clicked.connect(self.confirmStart)

    def update_svg_file(self, whichBox):
        if whichBox == "PHOTO":
            selected_file = self.photo_cbox.currentText()
            config.PHOTO_FILE = os.path.join("svg_images", selected_file)
            self.photo_text_file.setText(f'Image File: {config.PHOTO_FILE}')
            self.DLP_preview_scene.removeItem(self.photo_svg)
            self.photo_svg = QGraphicsSvgItem(config.PHOTO_FILE)
            self.DLP_preview_scene.addItem(self.photo_svg)
            self.photo_svg.setZValue(2)
            
        if whichBox == "ALIGN":
            selected_file = self.assist_cbox.currentText()
            config.ALIGNMENT_FILE = os.path.join("svg_images", selected_file)
            self.assist_text_file.setText(f'Image File: {config.ALIGNMENT_FILE}')
            self.DLP_preview_scene.removeItem(self.align_svg)
            self.align_svg = QGraphicsSvgItem(config.ALIGNMENT_FILE)
            self.DLP_preview_scene.addItem(self.align_svg)
            self.align_svg.setZValue(1)

        # Apply a colorize effect
        photo_colorize_effect = QGraphicsColorizeEffect()
        photo_colorize_effect.setColor(QColor(0, 0, 255)) # Complete blue filter on all photo layers.
        photo_colorize_effect.setStrength(1)
        self.photo_svg.setGraphicsEffect(photo_colorize_effect)
        self.align_svg.setGraphicsEffect(photo_colorize_effect)
    
    def confirmStart(self):
        warning = QMessageBox()
        warning_text = f"""
            CAUTION! UV LEDs are about to turn on. 
            Ensure the working area is clear and 
            eye protection is being used.

            \nSelected Exposure Time: {self.exposure_spinbox.value()} seconds
            \nUV Brightness: {self.photo_slider_UV.value()} ({self.photo_slider_UV.value()*100//255}%)

            \nCONFIRM UV EXPOSURE:
        """
        warning.setText(warning_text)
        icon = QMessageBox.Icon.Warning
        warning.setIcon(icon)
        warning.setWindowTitle("CONFIRM UV EXPOSURE")
        confirmButton = QMessageBox.StandardButton.Yes
        cancelButton = QMessageBox.StandardButton.Cancel
        warning.setStandardButtons(confirmButton | cancelButton)
        warning.setDefaultButton(cancelButton)
        warning.button
        button = warning.exec()

        if button == confirmButton:
            startPhotoLithography()
        if button == cancelButton:
            print("Canceled.")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, a0):
        exit() # Close the whole program if the main window is closed.
        # NOTE: The default splash of the DLP MUST be a black screen, or something with NO blue.
        #       Otherwise, it will emit UV light when the splash screen (or "No-signal" screen) takes over.


class DLP():
    def __init__(self):
        try:
            self.screen_geometry = QApplication.screens()[1].geometry()
            self.width = self.screen_geometry.width()
            self.height = self.screen_geometry.height()
        except IndexError:
            self.screen_geometry = QApplication.screens()[0].geometry()
            self.width = self.screen_geometry.width()
            self.height = self.screen_geometry.height()
            print("Only one display detected; showing image on primary display.")
        except Exception as e:
            print(e)

class LithoWindow(QMainWindow): # Create the window that the DLP will receieve
    def __init__(self, parentWindow):
        super().__init__()
        self.setWindowTitle("Image")

        # Attempt to move image to second display
        try:
            
            self.setGeometry(DLP.screen_geometry)
            self.showFullScreen()
            if DLP.width < config.LITHO_SIZE_PX_X or DLP.height < config.LITHO_SIZE_PX_Y:
                print("Warning: Second display resolution is smaller than lithography image size.")
                print("Image cropped to:")
                # Set to a square ratio based on max screen height
                config.LITHO_SIZE_PX_Y = DLP.height
                config.LITHO_SIZE_PX_X = DLP.height
                print(f"\tWidth: {config.LITHO_SIZE_PX_X} px")
                print(f"\tHeight: {config.LITHO_SIZE_PX_Y} px")

        except Exception as e:
            print(e)

        self.DLP_view = QGraphicsView(parentWindow.DLP_preview_scene, self)
        self.DLP_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.DLP_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.blackout_scene = QGraphicsScene()
        self.blackout_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0))) # Complete blackout
        self.blackout_view = QGraphicsView(self.blackout_scene)
        self.blackout_view.setAutoFillBackground(True)
        self.blackout_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.blackout_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.blackout_view)

def startPhotolithography():
    print("Starting UV exposure...")


app = QApplication(sys.argv)

DLP = DLP()
mainWindow = MainWindow()
mainWindow.show()

lithoWindow = LithoWindow(mainWindow)
lithoWindow.show()

app.exec()