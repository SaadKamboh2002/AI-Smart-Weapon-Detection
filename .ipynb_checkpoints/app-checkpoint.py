# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 00:20:35 2025

@author: Saad Amir Sohail
"""

import tkinter as tk
from tkinter import filedialog, Label, Button, Canvas
from PIL import Image, ImageTk
# import cv2
# import torch
import os
from ultralytics import YOLO

# loading model
model = YOLO(os.getcwd()+'/best.pt')

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[('Image/Video Files', '*.jpg;*.png;*.mp4')])
    if file_path:
        file_label.config(text=f"Selected: {file_path}")
        process_file(file_path)

def process_file(file_path):
    img = Image.open(file_path) if file_path.endswith(('jpg', 'png')) else None
    
    if img:
        img.thumbnail((400, 400))
        img = ImageTk.PhotoImage(img)
        canvas.create_image(200, 200, anchor=tk.CENTER, image=img)
        canvas.image = img  # Keep reference to avoid garbage collection
    
    # performing detection
    results = model(file_path)
    results.show()  # show detection result (for testing)
    results.save(save_dir="detections/")  # Save detection results

    result_label.config(text="Detection Complete! Check 'detections/' folder.")

# creating UI window
root = tk.Tk()
root.title("Smart Behavior and Weapon Detection System")
root.geometry("500x600")

Label(root, text="Smart Behavior and Weapon Detection System", font=("Arial", 16)).pack(pady=10)
Button(root, text="Select Image/Video", command=select_file).pack(pady=5)
file_label = Label(root, text="No file selected", fg="blue")
file_label.pack()

canvas = Canvas(root, width=400, height=400, bg="gray")
canvas.pack(pady=10)

result_label = Label(root, text="", fg="green")
result_label.pack()

root.mainloop()