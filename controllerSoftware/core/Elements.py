import os
import sys

import tkinter as tk

from tkinter import filedialog


class Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        

def resourcePath(relativePath):
    
    return relativePath
    
    basePath = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)


def tempText(event, entry_widget, originalEntry):
	if entry_widget.get() == originalEntry:
		event.widget.delete(0,'end')

