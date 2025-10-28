# ...existing code...
import tkinter as tk
import sqlite3
import os
import tkinter.messagebox as messagebox
# ...existing code...

# ウィンドウの作成
root = tk.Tk()
root.title("単語一覧")
root.geometry("1000x700")

# 単語リストの表示
word_listbox = tk.Listbox(root, font=("Helvetica", 36))
word_listbox.pack(fill=tk.BOTH, expand=True)

# DBパス（プロジェクト内の data/words.db を想定）
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'words.db')

def load_words():
    """DBから単語を読み込み、Listboxに表示する。存在しなければサンプルを表示。"""
    word_listbox.delete(0, tk.END)
    if not os.path.exists(DB_PATH):
        # DBが無ければサンプルデータを表示
        sample = ["apple", "banana", "cherry", "date", "elderberry",
                  "fig", "grape", "honeydew", "kiwi", "lemon", "mango"]
        messagebox.showwarning("警告", f"DBが見つかりません: {DB_PATH}\nサンプルデータを表示します。")
        for w in sample:
            word_listbox.insert(tk.END, w)
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # テーブル名を 'words'、カラムを 'word' と想定
        cur.execute("SELECT word FROM words ORDER BY word;")
        rows = cur.fetchall()
        if not rows:
            messagebox.showinfo("情報", "DBに単語が登録されていません。")
        for r in rows:
            word_listbox.insert(tk.END, r[0])
    except Exception as e:
        messagebox.showerror("DBエラー", str(e))
    finally:
        try:
            conn.close()
        except:
            pass

# 読み込みボタン（更新）
refresh_btn = tk.Button(root, text="更新", command=load_words)
refresh_btn.pack(side=tk.BOTTOM, pady=6)

# 初回読み込み
load_words()

# メインループの開始
root.mainloop()
# ...existing code...