import tkinter as tk
from tkinter import ttk

# --- グローバル状態管理変数 ---
name_visibility = 1         # 1:表示, 0:非表示
description_visibility = 1  # 1:表示, 0:非表示
# -----------------------------

Wordbook = tk.Tk()
Wordbook.title("WordBookPage")

# データベースから受け取ったデータ（実際の値）
wN = "ベルクマンの法則"
wD = "恒温動物においては、同じ種でも寒冷な地域に生息するものほど体重が大きく、近縁な種間では大型の種ほど寒冷な地域に生息する、という法則。\n類似のものにアレンの法則というものがあり、こちらは寒冷地ほど表面積が小さくなるというものである。"

# --- Tkinter変数 (StringVar) の初期化 ---
# ラベルとボタンのテキストを動的に変更するために必要
wordName_var = tk.StringVar(value=wN)
wordDescription_var = tk.StringVar(value=wD)
btnName_var = tk.StringVar(value="名前を隠す")
btnDescription_var = tk.StringVar(value="説明を隠す")


# ----------------------------------------------------
# ★ 表示・非表示ボタンを押された際に呼び出される関数
# ----------------------------------------------------

# 名前表示・非表示ボタン
def visibility_name_click():
    global name_visibility # グローバル変数を関数内で変更できるように宣言
    
    if name_visibility == 1:
        # 非表示にする (現在表示中)
        name_visibility = 0
        wordName_var.set("???") # ★ ラベルのテキストを更新
        btnName_var.set("名前を見る") # ★ ボタンのテキストを更新
    else:
        # 表示にする (現在非表示)
        name_visibility = 1
        wordName_var.set(wN) # ★ ラベルのテキストを実際のデータに戻す
        btnName_var.set("名前を隠す")

# 説明文表示・非表示ボタン
def visibility_description_click():
    global description_visibility
    
    if description_visibility == 1:# 非表示にする (現在表示中)
        description_visibility = 0
        wordDescription_var.set("???")
        btnDescription_var.set("説明を見る")
    else:# 表示にする (現在非表示)
        description_visibility = 1
        wordDescription_var.set(wD)
        btnDescription_var.set("説明を隠す")

# ----------------------------------------------------
# ★ ウィジェットの定義 (StringVarを使用するように変更)
# ----------------------------------------------------
label1 = ttk.Label(Wordbook, textvariable=wordName_var)
label2 = ttk.Label(Wordbook, textvariable=wordDescription_var)

# textの代わりに textvariable を使用
visNameBTN = ttk.Button(Wordbook, textvariable=btnName_var, command=visibility_name_click)
visDescriptionBTN = ttk.Button(Wordbook, textvariable=btnDescription_var, command=visibility_description_click)

backPageBTN = ttk.Button(Wordbook, text="前のページへ")
nextPageBTN = ttk.Button(Wordbook, text="次のページへ")
goHomeBTN = ttk.Button(Wordbook, text="homeへ戻る")

# ----------------------------------------------------
# 実際に配置する
# ----------------------------------------------------
label1.pack(pady=10)
visNameBTN.pack(pady=(4,10))
label2.pack(padx=(20,20),pady=(20,20))
visDescriptionBTN.pack(pady=(4,20))

backPageBTN.pack(side=tk.LEFT,padx=10,pady=10)
nextPageBTN.pack(side=tk.RIGHT,padx=10,pady=10)
goHomeBTN.pack(pady=10)

Wordbook.mainloop()