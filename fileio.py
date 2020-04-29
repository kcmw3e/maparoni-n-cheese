################################################################################
#
#   fileio.py
#   Code by: Casey Walker
#
################################################################################

#Adapted from:
#https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python

import tkinter as tk
from tkinter import filedialog

def open_file_string():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    with open(file_path) as f:
        read_data = f.read()
    return read_data

def save_file_string(string):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename()
    with open(file_path, "w") as f:
        f.write(string)