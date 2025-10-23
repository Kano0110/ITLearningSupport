import tkinter as tk
from tkinter import ttk  # ttkはよりモダンなウィジェットを提供します

# 1. ルートウィンドウの作成
# 'tk.Tk()'がアプリケーションのメインウィンドウを作成します
root = tk.Tk()
root.title("HOME") # ウィンドウのタイトルを設定

# 2. ウィジェットの作成と配置

# ラベル（テキスト表示）の作成
label = ttk.Label(root, text="HOME")
# ウィンドウ内にウィジェットを配置 ('pack'は最も簡単な配置方法です)
label.pack(padx=20, pady=10) # 垂直方向(pady)と水平方向(padx)に余白を追加

# ボタンの作成
button = ttk.Button(root, text="単語帳を作る")
button.pack(pady=10)

button = ttk.Button(root, text="単語帳を見る")
button.pack(pady=10)

button = ttk.Button(root, text="問題を解く")
button.pack(pady=10)

# 3. メインループの開始
# アプリケーションが動作し、ユーザーのイベントを待ち受ける状態になります
root.mainloop()