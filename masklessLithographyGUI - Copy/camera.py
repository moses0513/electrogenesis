# Used for testing live footage from the basler camera
# for the maskless photolithography machine.
# The footage needs to be in the form of a PyQt5 widget.
# Otherwise, this can be done with a simple OpenCV window.
# Updated 1/20/2025 by S. Jacob Finch
# 
# Thanks to Google and 'eyllanesc' on stack overflow

from PyQt6.QtWidgets import  QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
import sys
import cv2

class Thread(QThread):
    updatePixmap = pyqtSignal(QImage)

    def run(self):
        # Try to open the basler camera
        try:
            # Index will vary based on system.
            # For a laptop, the built-in webcam is usually 0.
            # Sometimes it takes a few seconds to appear.
            cap = cv2.VideoCapture(0) 
        except Exception as e:
            print(f"Exception: {e}")
            print("No camera found.")
            return
        # Continuously get frames from the camera
        while True:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.updatePixmap.emit(p)

class CameraFeed(QWidget):
    def __init__(self):
        super().__init__()
        # Make a label to hold the camera feed
        self.label = QLabel(self)
        self.label.resize(640, 480)
        # Use threading to continuously update the camera
        th = Thread(self)
        th.updatePixmap.connect(self.setImage)
        th.start()
        self.show()
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

# app = QApplication(sys.argv)
# camFeed = CameraFeed()
# camFeed.show()
# app.exec()