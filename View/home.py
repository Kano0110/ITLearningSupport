import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("HOME")

# ラベルの作成
label = ttk.Label(root, text="HOME")
label.pack(padx=20, pady=10) 

# ボタンの作成
button = ttk.Button(root, text="単語帳を作る")
button.pack(pady=10)

button = ttk.Button(root, text="単語帳を見る")
button.pack(pady=10)

button = ttk.Button(root, text="問題を解く")
button.pack(pady=10)

root.mainloop()