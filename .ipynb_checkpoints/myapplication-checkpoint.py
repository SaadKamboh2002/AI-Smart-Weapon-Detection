# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 00:05:28 2025

@author: Amir Sohail
"""

import tkinter as tk

root = tk.Tk()
root.title('AI Smart Weapon and Behavior Detection')
root.geometry('720x440')

label = tk.Label(root, text='Enter Name') # a prompt to enter name
label.pack() # this places the entry field inside the window

entry = tk.Entry(root)
entry.pack()

def on_click():
    user_text = entry.get()  # get text from entry field
    label.config(text=f"Hello, {user_text}!")  # update label

button = tk.Button(root, text="Submit", command=on_click)
button.pack()

root.mainloop()
