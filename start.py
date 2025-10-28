# start.py

import tkinter as tk
# 正しいパスでController内のAppControllerをインポート
# パッケージ名 (Controller) の中にある WordbookController モジュールから AppController クラスをインポート
from Controller.WordbookController import AppController

if __name__ == "__main__":
    print("Application starting...")
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()
