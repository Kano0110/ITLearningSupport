# View/WordEntryView.py
import tkinter as tk
from tkinter import ttk, messagebox

class WordEntryView:
    """単語登録画面の View。controller を受け取り、ボタン操作は controller のメソッドを呼ぶ。"""

    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        
        self.style = ttk.Style()
        # メインフレーム
        self.frame = ttk.Frame(self.root)

        vcmd = (self.frame.register(self._validate_hiragana), "%P")
        
        # ウィジェット定義
        self.entry_Name = ttk.Entry(self.frame, width=40)
        self.entry_Yomi = ttk.Entry(self.frame, width=40, validate="key", validatecommand=vcmd)
        
        self.entry_Kai = tk.Text(self.frame, width=40, height=10)
        
        # Combobox (state='normal' などの指定なし = デフォルトで入力も選択も可能)
        self.cb_Category = ttk.Combobox(self.frame, values=[], width=17)
        self.cb_Tag = ttk.Combobox(self.frame, values=[], width=17)
        
        self._build_ui()

    def _build_ui(self):
        # self.root.title("単語登録") # AppController側で制御するため削除しても良いが残しておく

        self.style.configure("My.TButton", foreground="#ff0000")

        # place を使用したレイアウト (ウィンドウサイズ固定前提)
        ttk.Label(self.frame, text='単語名：').place(x=60, y=30)
        self.entry_Name.place(x=150, y=30)

        ttk.Label(self.frame, text='ふりがな：').place(x=59, y=60)
        self.entry_Yomi.place(x=150, y=60)

        ttk.Label(self.frame, text='解説：').place(x=65, y=120)
        self.entry_Kai.place(x=150, y=90)
        
        ttk.Label(self.frame, text='カテゴリ').place(x=70, y=260)
        self.cb_Category.place(x=120, y=260)
        
        ttk.Label(self.frame, text='タグ').place(x=315, y=260)
        self.cb_Tag.place(x=350, y=260)
        
        ttk.Button(self.frame, text='単語一覧に戻る', command=lambda: self.controller.create_close_window()).place(x=40, y=340)
        ttk.Button(self.frame, text='リセット', style="My.TButton", command=lambda: self.controller.create_reset_window()).place(x=490, y=40)
        ttk.Button(self.frame, text='作成', command=lambda: self.controller.get_id_pass()).place(x=490, y=340)

        self.entry_Name.bind("<Return>", lambda e: self.entry_Yomi.focus_set())
        self.entry_Yomi.bind("<Return>", lambda e: self.entry_Kai.focus_set())
        self.entry_Kai.bind("<Return>", lambda e: None)  # 最後は何もしない

    def show(self):
        """この View を表示する（controller.show から呼ばれる）。"""
        # AppControllerのサイズ(600x500)に合わせて fill する
        self.frame.pack(expand=True, fill='both')

    def close(self):
        """表示を閉じる（pack_forget）。"""
        self.frame.pack_forget()

    def set_combo_values(self, categories: list, tags: list):
        """プルダウンの候補を設定する"""
        self.cb_Category['values'] = categories
        self.cb_Tag['values'] = tags

    def get_name(self):
        return self.entry_Name.get().strip()
    
    def get_yomi(self):
        return self.entry_Name.get().strip()
    
    def get_explain(self):
        return self.entry_Kai.get("1.0", "end-1c").strip()

    def get_category(self):
        return self.cb_Category.get().strip()

    def get_tag(self):
        return self.cb_Tag.get().strip()
    
    def _validate_hiragana(self, P):
        # P = 入力後の文字列
        if P == "":
            return True
        import re
        return bool(re.fullmatch(r"[ぁ-ゖー]*", P))

    def clear_inputs(self):
        """入力欄をクリアする（リセット処理）。"""
        self.entry_Name.delete("1.0", tk.END)
        self.entry_Yomi.delete("1.0", tk.END)
        self.entry_Kai.delete("1.0", tk.END)
        self.cb_Category.set("")
        self.cb_Tag.set("")

    def show_error(self, msg: str):
        messagebox.showerror("エラー", msg)

    def show_success(self, msg: str):
        messagebox.showinfo("完了", msg)