# SVG to HDMI output test

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from layout_colorwidget import Color

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Test app")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()