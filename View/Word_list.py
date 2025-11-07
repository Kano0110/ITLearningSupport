import tkinter as tk
import os
import tkinter.messagebox as messagebox
import sqlite3
import sys

# ウィンドウの作成
root = tk.Tk()
root.title("単語一覧")
root.geometry("1000x700")

# 単語リストの表示
word_listbox = tk.Listbox(root, font=("Helvetica", 16))
word_listbox.pack(fill=tk.BOTH, expand=True)

# サンプル単語データ
words = ["apple", "banana", "cherry", "date", "elderberry",
            "fig", "grape", "honeydew", "kiwi", "lemon", "mango"]
for word in words:
        word_listbox.insert(tk.END, word)

# 読み込みボタン（更新）
def refresh_words():
    word_listbox.delete(0, tk.END)
    for word in words:
        word_listbox.insert(tk.END, word)
refresh_btn = tk.Button(root, text="更新", command=refresh_words)
refresh_btn.pack(side=tk.BOTTOM, pady=6)

try:
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'data', 'words.db'))
    cur = con.cursor()
    cur.execute("SELECT word FROM words ORDER BY word;")
    rows = cur.fetchall()
    if rows:
        words = [r[0] for r in rows]

except Exception as e:
    messagebox.showerror("DBエラー", str(e))
    sys.exit(0)

# 初回読み込み
refresh_words()

# メインループの開始
root.mainloop()