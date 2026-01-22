import sys, os
import config, image_processing, camera
import gantryControl as gantry

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGraphicsScene, QGraphicsView,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QStackedLayout, QLabel, QComboBox,
    QSlider, QCheckBox, QSpinBox,
    QDoubleSpinBox, QPushButton,
    QSpacerItem, QMessageBox, QSizePolicy
)

from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QResizeEvent, QBrush, QColor


png_images = os.listdir("png_images")


class GraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def sizeHint(self):
        return QSize(400, 600)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EGEN Photolithography Settings")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        QApplication.setStyle("Fusion")

        self.layout_top = QHBoxLayout()
        self.layout_left = QVBoxLayout()
        self.layout_middle = QVBoxLayout()
        self.layout_right = QVBoxLayout()
        self.layout_stage = QGridLayout()

        # Stage buttons
        self.stage_x_up = QPushButton("X+")
        self.stage_x_down = QPushButton("X-")
        self.stage_y_up = QPushButton("Y+")
        self.stage_y_down = QPushButton("Y-")
        self.stage_z_up = QPushButton("Z+")
        self.stage_z_down = QPushButton("Z-")

        for b in [
            self.stage_x_up, self.stage_x_down,
            self.stage_y_up, self.stage_y_down,
            self.stage_z_up, self.stage_z_down
        ]:
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.layout_stage.addWidget(self.stage_y_up, 0, 1)
        self.layout_stage.addWidget(self.stage_x_down, 1, 0)
        self.layout_stage.addWidget(self.stage_x_up, 1, 2)
        self.layout_stage.addWidget(self.stage_y_down, 2, 1)
        self.layout_stage.addWidget(self.stage_z_up, 0, 2)
        self.layout_stage.addWidget(self.stage_z_down, 2, 2)

        self.layout_left.addLayout(self.layout_stage)

        # Preview
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view = GraphicsView(self.scene, self)

        self.layout_right.addWidget(self.view)

        self.layout_top.addLayout(self.layout_left)
        self.layout_top.addLayout(self.layout_middle)
        self.layout_top.addLayout(self.layout_right)

        central = QWidget()
        central.setLayout(self.layout_top)
        central.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCentralWidget(central)

        # Button bindings
        self.stage_x_up.clicked.connect(lambda: gantry.moveMOTOR("X+100"))
        self.stage_x_down.clicked.connect(lambda: gantry.moveMOTOR("X-100"))
        self.stage_y_up.clicked.connect(lambda: gantry.moveMOTOR("Y+100"))
        self.stage_y_down.clicked.connect(lambda: gantry.moveMOTOR("Y-100"))
        self.stage_z_up.clicked.connect(lambda: gantry.moveMOTOR("Z+100"))
        self.stage_z_down.clicked.connect(lambda: gantry.moveMOTOR("Z-100"))

    # 🔥 GUARANTEED keyboard capture
    def keyPressEvent(self, event):
        key = event.key()

<<<<<<< HEAD
        if key == Qt.Key.Key_Up:
            gantry.moveMOTOR("Y+100")
        elif key == Qt.Key.Key_Down:
            gantry.moveMOTOR("Y-100")
        elif key == Qt.Key.Key_Left:
            gantry.moveMOTOR("X-100")
        elif key == Qt.Key.Key_Right:
            gantry.moveMOTOR("X+100")
        elif key == Qt.Key.Key_PageUp:
            gantry.moveMOTOR("Z+50")
        elif key == Qt.Key.Key_PageDown:
            gantry.moveMOTOR("Z-50")
        else:
            super().keyPressEvent(event)

=======
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
        # Update Align image
        selected_file = self.assist_cbox.currentText()
        config.ALIGNMENT_FILE = os.path.join("png_images", selected_file)
        self.assist_text_file.setText(f'Image File: {config.ALIGNMENT_FILE}')

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
            print("Canceled.")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, a0):
        exit() # Close the whole program if the main window is closed.
        # NOTE: The default splash of the DLP MUST be a black screen, or something with NO blue.
        #       Otherwise, it will emit UV light when the splash screen (or "No-signal" screen) takes over.

    def startPhotolithography(self):
        print("Starting UV exposure...")
        lithoWindow.DLP_scene = self.DLP_preview_scene
        # lithoWindow.DLP_scene = QGraphicsScene()
        # lithoWindow.DLP_scene.addItem(self.photo_and_align_graphics_item)
        lithoWindow.DLP_view = QGraphicsView(lithoWindow.DLP_scene, self)
        lithoWindow.DLP_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lithoWindow.DLP_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lithoWindow.setCentralWidget(lithoWindow.DLP_view)

    def stopPhotolithography(self):
        print("STOPPING UV exposure.")
        lithoWindow.blackout()

class DLP():
    def __init__(self):
        try: # Try to connect to the DLP as the second display.
            self.screen_geometry = QApplication.screens()[1].geometry()
            self.width = self.screen_geometry.width()
            self.height = self.screen_geometry.height()
            self.connected = True
            print(self.screen_geometry)
        except IndexError:
            self.connected = False
            self.width = 0
            self.height = 0
            # self.screen_geometry = QApplication.screens()[0].geometry()
            # self.width = self.screen_geometry.width()
            # self.height = self.screen_geometry.height()
            # print("Only one display detected; showing image on primary display.")
            print("No second display detected. Running GUI only.")
        except Exception as e:
            print(e)

class LithoWindow(QMainWindow): # Create the window that the DLP will receieve
    def __init__(self, parentWindow):
        super().__init__()
        self.setWindowTitle("Image")

        # Attempt to move image to second display
        if DLP.connected:
            try:
                self.setGeometry(DLP.screen_geometry)
                self.showFullScreen()
                if DLP.width < config.LITHO_SIZE_PX_X or DLP.height < config.LITHO_SIZE_PX_Y:
                    print("Warning: Second display resolution is smaller than lithography image size.")
                    print("Cropping images to:")
                    # Set to a square ratio based on max screen height
                    config.LITHO_SIZE_PX_Y = DLP.height
                    # config.LITHO_SIZE_PX_X = DLP.height
                    print(f"\tWidth: {config.LITHO_SIZE_PX_X} px")
                    print(f"\tHeight: {config.LITHO_SIZE_PX_Y} px")

            except Exception as e:
                print(e)
        
        # Finish setting up the window by blacking everything out.
        self.blackout()

    def blackout(self):
        self.blackout_scene = QGraphicsScene()
        self.blackout_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0))) # Total darkness *evil laugh*
        self.blackout_view = QGraphicsView(self.blackout_scene)
        self.blackout_view.setAutoFillBackground(True)
        self.blackout_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.blackout_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.blackout_view)


>>>>>>> jacob

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
