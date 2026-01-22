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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
