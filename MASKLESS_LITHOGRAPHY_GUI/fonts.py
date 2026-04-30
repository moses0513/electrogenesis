from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication
a = QApplication([])
fonts = QFontDatabase.families()
print(fonts)
