import tkinter as tk

from pages.ControlerGUI import ControlerGUI
from core.Elements import resourcePath


class MainApp(tk.Tk):
    
    
    def __init__(self):
        
        super().__init__()
        
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        
        self.windowWidth = 400 # <----- Enter Window Width Here
        self.windowHeight = 600 # <----- Enter Window Height Here

        windowDimensions = f'{self.windowWidth}x{self.windowHeight}+{int((self.screenWidth-self.windowWidth)/2)}+{int((self.screenHeight-self.windowHeight)/3)}'

        self.title("Maskless Lithography Stage Controller") # <----- Enter Title Here
        self.geometry(windowDimensions) # <----- Enter Geometry Here
        self.resizable(False, False)
        self.config(bg="#5E5E5E") # Background color

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        logoPath = resourcePath('./assets/egenLogo.ico')
        self.iconbitmap(logoPath)

        # ================== Enter Variables Here ==================


        # ==========================================================
        
        self.frames = {}
        self.frameList = [ControlerGUI] # <----- Enter Names of Frames
        
        for f in self.frameList:

            page_name = f.__name__
            frame = f(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(self.frameList[0].__name__)
        
        
    def showFrame(self, page_name):
        
        frame = self.frames[page_name]
        frame.tkraise()
