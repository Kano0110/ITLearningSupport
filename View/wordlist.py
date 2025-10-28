# ...existing code...
import tkinter as tk
from tkinter import ttk
import sqlite3
import os
import tkinter.messagebox as messagebox

DB_FILE = "terms.db"
MAX_ROWS_PER_COLUMN = 20  # 1列あたりの最大行数

# 読み仮名マップ（各行の先頭文字群）
YOMI_MAP = {
    'あ': ('あ', 'い', 'う', 'え', 'お'),
    'か': ('か', 'き', 'く', 'け', 'こ'),
    'さ': ('さ', 'し', 'す', 'せ', 'そ'),
    'た': ('た', 'ち', 'つ', 'て', 'と'),
    'な': ('な', 'に', 'ぬ', 'ね', 'の'),
    'は': ('は', 'ひ', 'ふ', 'へ', 'ほ'),
    'ま': ('ま', 'み', 'む', 'め', 'も'),
    'や': ('や', 'ゆ', 'よ'),
    'ら': ('ら', 'り', 'る', 'れ', 'ろ'),
    'わ': ('わ', 'を', 'ん'),
}

# DBパス候補
DB_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), '..', 'data', DB_FILE),
    os.path.join(os.path.dirname(__file__), DB_FILE),
    DB_FILE
]

def find_db_path():
    for p in DB_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def fetch_terms(category=None):
    """DB から name（表示単語）を文字列リストで返す。
    category が与えられればその行のみを取得。None で全件。
    """
    db_path = find_db_path()
    if not db_path:
        # DB が見つからない場合は空リストを返す
        return []
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        if category and category in YOMI_MAP:
            placeholders = ','.join('?' * len(YOMI_MAP[category]))
            params = tuple(YOMI_MAP[category])
            sql = f"SELECT name, yomi FROM terms WHERE SUBSTR(yomi,1,1) IN ({placeholders}) ORDER BY yomi;"
            cur.execute(sql, params)
        else:
            sql = "SELECT name, yomi FROM terms ORDER BY yomi;"
            cur.execute(sql)
        rows = cur.fetchall()
        # name列だけを返す（存在しないカラムなら例外で空に落ちる）
        names = [r[0] for r in rows]
        return names
    except Exception as e:
        # DBスキーマが違う等のエラーは空リストで扱う
        print("DBエラー:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

# GUI 状態
current_category = None     # 選択中の行（'あ','か',... または None）
all_terms = []              # DB の全件キャッシュ
current_terms = []          # 現在の行で取得したリスト（行選択時）
# UI 作成
root = tk.Tk()
root.title("IT用語辞書")
root.geometry("600x440")

# 上部: 索引ボタン
index_frame = ttk.Frame(root, padding=8)
index_frame.pack(fill='x')
indices = ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ']

def on_index_click(category):
    global current_category, current_terms
    current_category = category
    current_terms = fetch_terms(category)
    apply_filter_and_display()

for idx in indices:
    b = ttk.Button(index_frame, text=idx, width=3, command=lambda c=idx: on_index_click(c))
    b.pack(side='left', padx=2)

# 検索バー
search_frame = ttk.Frame(root, padding=(8,4))
search_frame.pack(fill='x')
ttk.Label(search_frame, text="絞り込み:").pack(side='left')
search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side='left', padx=(6,4))

def clear_search():
    search_var.set("")
clear_btn = ttk.Button(search_frame, text="クリア", command=clear_search)
clear_btn.pack(side='left')

# リスト表示（Canvas + Frame でスクロール）
list_frame = ttk.Frame(root, padding=8)
list_frame.pack(expand=True, fill='both')

canvas = tk.Canvas(list_frame)
v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
canvas.configure(yscrollcommand=v_scroll.set)

canvas.grid(row=0, column=0, sticky='nsew')
v_scroll.grid(row=0, column=1, sticky='ns')
list_frame.rowconfigure(0, weight=1)
list_frame.columnconfigure(0, weight=1)

scrollable_frame = ttk.Frame(canvas)
canvas.create_window((0,0), window=scrollable_frame, anchor='nw')


def display_terms(terms, empty_message=None):
    # 既存ウィジェットを削除
    for w in scrollable_frame.winfo_children():
        w.destroy()
    if terms:
        for i, name in enumerate(terms):
            row_index = i % MAX_ROWS_PER_COLUMN
            col_index = i // MAX_ROWS_PER_COLUMN
            lbl = ttk.Label(scrollable_frame, text=name, padding=(4,2))
            lbl.grid(row=row_index, column=col_index, sticky='w')
    else:
        # empty_message が与えられればそれを優先、なければ既存の振る舞い
        if empty_message is None:
            if current_category:
                msg = f"{current_category}行の用語はありません"
            else:
                msg = "該当する用語はありません"
        else:
            msg = empty_message
        ttk.Label(scrollable_frame, text=msg).grid(row=0, column=0, sticky='w')
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def apply_filter_and_display(*_):
    """検索は全単語から絞り込む。検索空欄時は選択行（あ行等）を優先表示。"""
    q = search_var.get().strip().lower()

    if q:
        # 検索は常に全件から（行選択は無視）
        filtered = [t for t in all_terms if q in t.lower()]
        # 検索で0件のときは汎用メッセージを表示
        display_terms(filtered, empty_message="該当する用語はありません")
    else:
        # 検索が空なら行選択があればその行のみ、なければ全件
        source = current_terms if current_category else all_terms
        display_terms(list(source))

# 検索文字列変更を監視
search_var.trace_add('write', apply_filter_and_display)

# 初期ロード: 全件キャッシュ取得＆初期表示（全件）
all_terms = fetch_terms(None)
current_terms = []  # 行選択なし
apply_filter_and_display()

root.mainloop()
# ...existing code...