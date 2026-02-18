# Main GUI Window
# This file runs the main window for the maskless photolithography process.
# With the GUI, you can do the following:
# - View live microscopic camera footage of the stage (the wafer on the vacuum chuck)
# - Move the stage (aka the gantry) in X, Y, and Z directions, and return to the datum
# - Select the image to be exposed onto the wafer
# - Adjust brightness of the UV LEDs
# - Adjust brightness of the red/green LEDs, which are used to align the wafer prior to exposing
# - Preview the files and exposed areas that will be on the wafer
# - Set exposure time
# - Start and stop the exposure, with a UV safety warning that must be confirmed before starting.


"""
TO-DO:

X Change SVG code to PNG code
X Make SVGs update when new photo/assist files are selected from GUI
X Make second window reflect preview window
X Fix broken preview (happened right after adding DLP_preview_view to second display)
_ Prevent scrolling on DLP window
X Dialog box to confirm start or cancel
X Update aligment assist layers on second monitor 
X Color filtering
_ Runtime dialog with stopwatch, goal
_ Fix config values not updating (images do not crop. use a different strategy for global vars? re-grab the config file?)
_ Add a displayAlignmentImage() function that connects to the "Draw alignment image on wafer" checkbox

Perhaps:
_ Prevent dragging window into DLP or moving mouse onto it... Might get really technical

"""

import sys, os, time
import config, image_processing, camera, stage_controller
import gantryControl as gantry
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QGraphicsScene,
    QGraphicsColorizeEffect,
    QGraphicsView,
    QVBoxLayout, 
    QHBoxLayout,
    QGridLayout,
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
# from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import Qt, QSize, QRectF, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QResizeEvent, QBrush, QColor

current_dir = os.path.dirname(os.path.abspath(__file__))
png_images = os.listdir(os.path.join(current_dir, "png_images"))
screens = QApplication.screens()

class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        # Fixed aspect ratio for the viewport
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
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
        self.fitInView(self.windowRect, Qt.AspectRatioMode.KeepAspectRatio)

    

class MainWindow(QMainWindow): # Main GUI for controlling photolithography settings and image
    @pyqtSlot(QThread) # Designate this as a slot for threading
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
        # Three sections, left, middle, and right
        # Left: Live camera footage, stage controller
        # Middle: Maskless lithography settings, Visual aligment assist settings
        # Right: Maskless lithography preview, Toggle circle color selectors
        self.layout_top = QHBoxLayout()
        self.layout_left = QVBoxLayout()
        self.layout_middle = QVBoxLayout()
        self.layout_right = QVBoxLayout()
        self.layout_exposure = QHBoxLayout()
        self.layout_circle = QHBoxLayout()
        self.layout_circle_dia = QVBoxLayout()
        self.layout_circle_offset_x = QVBoxLayout()
        self.layout_circle_offset_y = QVBoxLayout()
        self.layout_svg_preview = QStackedLayout()

        # LEFT
        # Camera feed and stage controller
        self.camera_label = QLabel("Live Camera Footage")
        self.camFeed = camera.CameraFeed()
        self.camFeed.setFixedSize(640, 480)

        self.layout_left.addWidget(self.camFeed)

        # MIDDLE
        # Stage controller for the stepper motors and magnetic encoders
        self.stage_controller = stage_controller.StageController()
        self.layout_middle.addWidget(self.stage_controller)
        
        # RIGHT
        # Photolithography preview
        # Make a miniature scene that replicates the DLP output
        self.preview_text_title = QLabel("Photolithography Preview:")
        QLabel.setAlignment(self.preview_text_title, Qt.AlignmentFlag.AlignCenter)

        self.DLP_preview_scene = QGraphicsScene()
        self.DLP_preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0))) # Complete blackout background
        self.DLP_preview_scene.setSceneRect(0, 0, config.LITHO_SIZE_PX_X//4, config.LITHO_SIZE_PX_Y//4)
        self.photo_and_align_graphics_item = image_processing.add_images(
            os.path.join(current_dir, config.PHOTO_FILE), 
            os.path.join(current_dir, config.ALIGNMENT_FILE)
        ) # Return a combined RGB image from photo and align layers
        self.DLP_preview_scene.addItem(self.photo_and_align_graphics_item)
        self.DLP_preview_view = GraphicsView(self.DLP_preview_scene, self)
        self.DLP_preview_view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # self.DLP_preview_view.heightForWidth(config.LITHO_SIZE_PX_Y//config.LITHO_SIZE_PX_X*300)
        # self.DLP_preview_view.setFixedSize(640, 640)
        # self.DLP_preview_view.scale(3, 3)
        # self.DLP_preview_view.fitInView(self.DLP_preview_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        

        # Output resolution:
        self.resolution_label = QLabel(f"Output resolution: {DLP.width} x {DLP.height}")
        
        # Exposure time
        self.exposure_label = QLabel("Exposure Time:")

        # Exposure time spinbox
        self.exposure_spinbox = QDoubleSpinBox()
        self.exposure_spinbox.setRange(0, 30)
        self.exposure_spinbox.setValue(config.EXPOSURE_TIME)
        self.exposure_spinbox.suffix = " sec"
        self.exposure_spinbox.setDecimals(2)

        # Exposure start/stop buttons
        self.exposure_STOP = QPushButton("STOP")
        self.exposure_STOP.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exposure_START = QPushButton("START")
        self.exposure_START.setStyleSheet("background-color: green; color: white; font-weight: bold;")

        # Alignment PNG layer
        self.alignment_draw_checkbox = QCheckBox("Draw alignment image on wafer")
        self.alignment_draw_checkbox.setChecked(True)

        # Alignment circle layer
        # self.alignment_circle_checkbox = QCheckBox("Draw alignment circle on wafer")
        # self.alignment_circle_text = QLabel("Aligment circle settings:")

        # self.alignment_circle_spinbox_dia_label = QLabel("Diameter (px):")
        # self.alignment_circle_spinbox_dia = QSpinBox()
        # self.alignment_circle_spinbox_dia.setRange(10, 2000)
        # self.layout_circle_dia.addWidget(self.alignment_circle_spinbox_dia_label)
        # self.layout_circle_dia.addWidget(self.alignment_circle_spinbox_dia)

        # self.alignment_circle_spinbox_offset_x_label = QLabel("Offset X (px):")
        # self.alignment_circle_spinbox_offset_x = QSpinBox()
        # self.alignment_circle_spinbox_offset_x.setRange(-1000, 1000)
        # self.layout_circle_offset_x.addWidget(self.alignment_circle_spinbox_offset_x_label)
        # self.layout_circle_offset_x.addWidget(self.alignment_circle_spinbox_offset_x)

        # self.alignment_circle_spinbox_offset_y_label = QLabel("Offset Y (px):")
        # self.alignment_circle_spinbox_offset_y = QSpinBox()
        # self.alignment_circle_spinbox_offset_y.setRange(-1000, 1000)
        # self.layout_circle_offset_y.addWidget(self.alignment_circle_spinbox_offset_y_label)
        # self.layout_circle_offset_y.addWidget(self.alignment_circle_spinbox_offset_y)

        # self.layout_circle.addLayout(self.layout_circle_dia)
        # self.layout_circle.addLayout(self.layout_circle_offset_x)
        # self.layout_circle.addLayout(self.layout_circle_offset_y)
        

        # Add widgets to RIGHT layout
        self.layout_right.addWidget(self.preview_text_title)
        self.layout_right.addWidget(self.DLP_preview_view)
        self.layout_right.addWidget(self.resolution_label)
        self.layout_exposure.addWidget(self.exposure_label)
        self.layout_exposure.addWidget(self.exposure_spinbox)
        self.layout_exposure.addWidget(self.exposure_STOP)
        self.layout_exposure.addWidget(self.exposure_START)
        self.layout_right.addLayout(self.layout_exposure)
        self.layout_right.addWidget(self.alignment_draw_checkbox)
        # self.layout_right.addWidget(self.alignment_circle_checkbox)
        # self.layout_right.addWidget(self.alignment_circle_text)
        # self.layout_right.addLayout(self.layout_circle)
        
        
        # Photolithography settings (outputs to UV LEDs)
        self.photo_text_title = QLabel("Photolithography Settings")
        QLabel.setAlignment(self.photo_text_title, Qt.AlignmentFlag.AlignCenter)

        self.photo_text_file = QLabel(f'Photolithography File: {config.PHOTO_FILE}')
        self.photo_cbox = QComboBox()
        self.photo_cbox.addItems(png_images)
        self.photo_cbox.setCurrentIndex(1)

        self.photo_text_UV = QLabel(f'UV LED Brightness: {config.BRIGHTNESS_UV}')
        self.photo_slider_UV = QSlider()
        self.photo_slider_UV.setOrientation(Qt.Orientation.Horizontal)
        self.photo_slider_UV.setMinimum(0)
        self.photo_slider_UV.setMaximum(255)
        self.photo_slider_UV.setValue(config.BRIGHTNESS_UV)

        # Alignment layer settings (can output to Red or Green LEDs)
        self.assist_text_title = QLabel("Alignment Settings")
        QLabel.setAlignment(self.assist_text_title, Qt.AlignmentFlag.AlignCenter)
        self.assist_text_file = QLabel(f'Image File: {config.PHOTO_FILE}')
        self.assist_cbox = QComboBox()
        self.assist_cbox.addItems(png_images)
        self.assist_cbox.setCurrentIndex(1)

        # Red and Green LED brightness sliders
        self.assist_text_RED = QLabel(f'Red LED Brightness: {config.BRIGHTNESS_RED}')
        self.assist_slider_RED = QSlider()
        self.assist_slider_RED.setOrientation(Qt.Orientation.Horizontal)
        self.assist_slider_RED.setMinimum(0)
        self.assist_slider_RED.setMaximum(255)
        self.assist_slider_RED.setValue(config.BRIGHTNESS_RED)

        self.assist_text_GREEN = QLabel(f'Green LED Brightness: {config.BRIGHTNESS_GREEN}')
        self.assist_slider_GREEN = QSlider()
        self.assist_slider_GREEN.setOrientation(Qt.Orientation.Horizontal)
        self.assist_slider_GREEN.setMinimum(0)
        self.assist_slider_GREEN.setMaximum(255)
        self.assist_slider_GREEN.setValue(config.BRIGHTNESS_GREEN)

        self.spacer = QSpacerItem(40, 40)

        # Add Photolithography widgets to layout
        self.layout_right.addWidget(self.photo_text_title)
        self.layout_right.addSpacerItem(self.spacer)
        self.layout_right.addWidget(self.photo_text_file)
        self.layout_right.addWidget(self.photo_cbox)
        self.layout_right.addWidget(self.photo_text_UV)
        self.layout_right.addWidget(self.photo_slider_UV)
        self.layout_right.addWidget(self.assist_text_title)
        self.layout_right.addWidget(self.assist_text_file)
        self.layout_right.addWidget(self.assist_cbox)
        self.layout_right.addWidget(self.assist_text_RED)
        self.layout_right.addWidget(self.assist_slider_RED)
        self.layout_right.addWidget(self.assist_text_GREEN)
        self.layout_right.addWidget(self.assist_slider_GREEN)
        self.layout_right.addSpacerItem(self.spacer)

        

        # Add the three main sections to the top-level layout
        self.layout_top.addLayout(self.layout_left)
        self.layout_top.addLayout(self.layout_middle)
        self.layout_top.addLayout(self.layout_right)
        # self.layout_top.insertSpacerItem(1, QSizePolicy.Expanding)

        # The MAIN widget that holds everything
        self.widget = QWidget()
        self.widget.setLayout(self.layout_top)
        self.setCentralWidget(self.widget)

        ############## Button Bindings ##############

        # Combo boxes
        self.photo_cbox.currentIndexChanged.connect(self.update_images)
        self.assist_cbox.currentIndexChanged.connect(self.update_images)
        # Sliders
        self.photo_slider_UV.sliderReleased.connect(self.update_UV_value) # Update images when released
        self.assist_slider_RED.sliderReleased.connect(self.update_RED_value)
        self.assist_slider_GREEN.sliderReleased.connect(self.update_GREEN_value)
        self.photo_slider_UV.valueChanged.connect(lambda: self.photo_text_UV.setText(f'UV LED Brightness: {self.photo_slider_UV.value()}')) # Update text while moving
        self.assist_slider_RED.valueChanged.connect(lambda: self.assist_text_RED.setText(f'Red LED Brightness: {self.assist_slider_RED.value()}'))
        self.assist_slider_GREEN.valueChanged.connect(lambda: self.assist_text_GREEN.setText(f'Green LED Brightness: {self.assist_slider_GREEN.value()}'))
        # Start/stop buttons
        self.exposure_START.clicked.connect(self.confirmStart)
        self.exposure_STOP.clicked.connect(self.stopPhotolithography)
        # Optional checkboxes
        self.alignment_draw_checkbox.stateChanged.connect(self.update_images)
        

    # Moses is working on this one, it blows up right now...
    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Up:
            gantry.moveMOTOR("Y+100")
        elif key == Qt.Key_Down:
            gantry.moveMOTOR("Y-100")
        elif key == Qt.Key_Left:
            gantry.moveMOTOR("X-100")
        elif key == Qt.Key_Right:
            gantry.moveMOTOR("X+100")
        elif key == Qt.Key_PageUp:
            gantry.moveMOTOR("Z+50")
        elif key == Qt.Key_PageDown:
            gantry.moveMOTOR("Z-50")
        else:
            super().keyPressEvent(event)

    def update_UV_value(self):
        value = self.photo_slider_UV.value()
        config.BRIGHTNESS_UV = value
        self.update_images()

    def update_RED_value(self):
        value = self.assist_slider_RED.value()
        config.BRIGHTNESS_RED = value
        self.update_images()

    def update_GREEN_value(self):
        value = self.assist_slider_GREEN.value()
        config.BRIGHTNESS_GREEN = value
        self.update_images()

    def update_images(self):
        # Update Photo image
        selected_file = self.photo_cbox.currentText()
        config.PHOTO_FILE = os.path.join("png_images", selected_file)
        self.photo_text_file.setText(f'Image File: {config.PHOTO_FILE}')
        # Update Align image (if different)
        if self.alignment_draw_checkbox.isChecked():
            selected_file = self.assist_cbox.currentText()
            config.ALIGNMENT_FILE = os.path.join("png_images", selected_file)
            self.assist_text_file.setText(f'Image File: {config.ALIGNMENT_FILE}')# Add the align image to the actual DLP_scene so we see it on the camera
            lithoWindow.align_graphics_item = image_processing.align_image(config.ALIGNMENT_FILE)
            lithoWindow.DLP_scene.addItem(lithoWindow.align_graphics_item)
        else:
            config.ALIGNMENT_FILE = None
            

        # Remove the old pixmap item, add a newly calculated one
        self.DLP_preview_scene.removeItem(self.photo_and_align_graphics_item)
        self.photo_and_align_graphics_item = image_processing.add_images(config.PHOTO_FILE, config.ALIGNMENT_FILE)
        self.DLP_preview_scene.addItem(self.photo_and_align_graphics_item)
        
        
    
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
            self.startPhotolithography()
        if button == cancelButton:
            print("Canceled Photolithography.")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, a0):
        exit() # Close the whole program if the main window is closed.
        # NOTE: The default splash of the DLP MUST be a black screen, or something with NO blue.
        #       Otherwise, it will emit UV light when the on-board splash screen (aka "No-signal" screen) takes over.

    def startPhotolithography(self):
        print("STARTING UV EXPOSURE...")
        
        # Add the image to be exposed
        lithoWindow.DLP_scene.removeItem(lithoWindow.photo_and_align_graphics_item)
        lithoWindow.photo_and_align_graphics_item = image_processing.add_images(config.PHOTO_FILE, config.ALIGNMENT_FILE)
        lithoWindow.DLP_scene.addItem(lithoWindow.photo_and_align_graphics_item)

        self.exposingThread = timedExposureThread(self.exposure_spinbox.value())
        self.exposingThread.endLitho.connect(self.stopPhotolithography)
        self.exposingThread.start()

    def stopPhotolithography(self):           
        lithoWindow.blackout()
        print("STOPPED UV EXPOSURE.")

class timedExposureThread(QThread):
    def __init__(self, EXPOSURE_TIME):
        super().__init__()
        self.EXPOSURE_TIME = EXPOSURE_TIME
    endLitho = pyqtSignal()
    def run(self):
        time.sleep(self.EXPOSURE_TIME)
        self.endLitho.emit()


class DLP():
    def __init__(self):
        try: # Try to connect to the DLP as the second display.
            self.screen = QApplication.screens()[1]
            self.screen_geometry = self.screen.geometry()
            self.width = self.screen_geometry.width()
            self.height = self.screen_geometry.height()
            self.connected = True
        except IndexError:
            self.connected = False
            self.width = 0
            self.height = 0
            print("No second display detected. Running GUI only.")
        except Exception as e:
            print(e)

class LithoWindow(QMainWindow): # Create the window that the DLP will receieve
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image")

        # Attempt to move image to second display
        if DLP.connected:
            try:
                self.setGeometry(DLP.screen_geometry)
                if DLP.width < config.LITHO_SIZE_PX_X or DLP.height < config.LITHO_SIZE_PX_Y:
                    print("Warning: Second display resolution is smaller than lithography image size.")
                    print("Cropping images to:")
                    # Set to a square ratio based on max screen height
                    config.LITHO_SIZE_PX_Y = DLP.height
                    # config.LITHO_SIZE_PX_X = DLP.height
                    print(f"\tWidth: {config.LITHO_SIZE_PX_X} px")
                    print(f"\tHeight: {config.LITHO_SIZE_PX_Y} px")

                self.DLP_scene = QGraphicsScene()
                self.photo_and_align_graphics_item = image_processing.align_image(config.ALIGNMENT_FILE)
                self.DLP_scene.addItem(self.photo_and_align_graphics_item)
                self.DLP_view = QGraphicsView(self.DLP_scene, self)
                self.DLP_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.DLP_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.DLP_view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.setCentralWidget(self.DLP_view)
            except Exception as e:
                print(e)
        
        # Finish setting up the window by blacking everything out.
        self.blackout()

    def blackout(self):
        self.blackout_scene = QGraphicsScene()
        self.blackout_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0))) # Total darkness.... *evil laugh*
        self.blackout_view = QGraphicsView(self.blackout_scene)
        self.blackout_view.setAutoFillBackground(True)
        self.blackout_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.blackout_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.blackout_view)



app = QApplication(sys.argv)

DLP = DLP()
mainWindow = MainWindow()
mainWindow.setGeometry(20, 60, 800, 600)
mainWindow.show()

lithoWindow = LithoWindow() # MAKE IT NOT A CHILD OF MAIN WINDOW????? <- will vars still work?
if DLP.connected:
    lithoWindow.show()
    # lithoWindow.move(DLP.screen_geometry.topLeft())
    mainWindow.showNormal()

# Note after doing all this: There's probably a better way to do all this. (P_P)

app.exec()