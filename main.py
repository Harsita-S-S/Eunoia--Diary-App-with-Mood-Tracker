import tkinter as tk
from login import setup_login
from diary import apply_background  

root = tk.Tk()
root.title("Eunoia")
root.state("zoomed")

image_path = "D:/Semester 2/spyder/package/final/eunoia_theme_bg.jpg"
root.after(100, lambda: apply_background(root, image_path)) 

setup_login(root)  

root.mainloop()
