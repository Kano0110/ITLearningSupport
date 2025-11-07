#start.py

import tkinter as tk
from Controller.AppController import AppController

if __name__ == "__main__":
    print("Application starting...")
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()