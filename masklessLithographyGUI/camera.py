# Used for testing live footage from the basler camera
# for the maskless photolithography machine.
# Updated for PyQt6

from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

import sys
import cv2


class CameraThread(QThread):
    updatePixmap = pyqtSignal(QImage)

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
        except Exception as e:
            print(f"Exception: {e}")
            print("No camera found.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Convert BGR → RGB
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w

            qtImage = QImage(
                rgbImage.data,
                w,
                h,
                bytesPerLine,
                QImage.Format.Format_RGB888
            )

            scaled = qtImage.scaled(
                640,
                480,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.updatePixmap.emit(scaled)


class CameraFeed(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Feed")

        self.label = QLabel(self)
        self.label.resize(640, 480)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.thread = CameraThread(self)
        self.thread.updatePixmap.connect(self.setImage)
        self.thread.start()

    @pyqtSlot(QImage)
    def setImage(self, image: QImage):
        self.label.setPixmap(QPixmap.fromImage(image))


# 🔎 Standalone test
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     camFeed = CameraFeed()
#     camFeed.show()
#     sys.exit(app.exec())
