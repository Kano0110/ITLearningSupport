import tkinter as tk

# ウィンドウの作成
root = tk.Tk()
root.title("My First App")
root.geometry("300x200")

# ラベルの作成
label = tk.Label(root, text="コントローラーでは、ビューからのリクエストを受け取り、モデルに処理を依頼します。")
label.pack(pady=20)

# メインループ
root.mainloop()