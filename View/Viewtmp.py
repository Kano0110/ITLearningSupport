import tkinter as tk

# ウィンドウの作成
root = tk.Tk()
root.title("My First App")
root.geometry("300x200")

# ラベルの作成
label = tk.Label(root, text="ビューでは、UIを担当しデータを表示します。")
label.pack(pady=20)

# メインループ
root.mainloop()