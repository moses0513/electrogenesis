import tkinter as tk

from PIL import Image, ImageTk 
from core.Elements import Page, resourcePath

class ControlerGUI(Page):
    
    def __init__(self, parent, controller):
        
        super().__init__(parent, controller)
        
        self.controller = controller
        self.config(bg="#5E5E5E")
        
        titleLabel = tk.Label(self, text="Stage Controller", fg="white", bg="#5E5E5E", font=("Arial", 16, "bold"))
        titleLabel.pack(pady=10)
        
        imagePath = resourcePath('./assets/egen25_logo.png')
        logoImage = Image.open(imagePath)
        logoImage = logoImage.resize((360, 170))
        logoImage = ImageTk.PhotoImage(logoImage)
        
        logoLabel = tk.Label(self, image=logoImage, bg="#5E5E5E")
        logoLabel.image = logoImage
        logoLabel.pack(pady=10)