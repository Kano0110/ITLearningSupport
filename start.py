import tkinter as tk
#import logging
#logging.basicConfig(level=logging.INFO)
from Controller.AppController import AppController

if __name__ == "__main__":
    print("Application starting...")
    root = tk.Tk()
    try:
        app = AppController(root)
    except Exception as e:
        print(f"FATAL: Failed to start AppController: {e}")
    else:
        root.mainloop()
