# View/WordEntryView.py
import tkinter as tk
from tkinter import ttk, messagebox

class WordEntryView:
    """単語登録画面の View"""

    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller

        self.style = ttk.Style()
        self.frame = ttk.Frame(self.root)
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)

        vcmd = (self.frame.register(self._validate_hiragana), "%P")

        # ウィジェット定義
        self.entry_Name = ttk.Entry(self.frame, width=40)
        self.entry_Yomi = ttk.Entry(self.frame, width=40, validate="key", validatecommand=vcmd)
        self.entry_Kai = tk.Text(self.frame, width=40, height=10)

        self.cb_Category = ttk.Combobox(self.frame, values=[], width=20)
        self.cb_Tag = ttk.Combobox(self.frame, values=[], width=20)

        self._build_ui()

    def _build_ui(self):
        # スタイル
        self.style.configure("Reset.TButton", foreground="#E4342E")
        self.style.configure("Create.TButton", foreground="#099945")
        self.style.configure("Back.TButton", foreground="#1523E6")

        # ===== タイトル =====

        title_frame = tk.Frame(self.frame, bg="#099945")
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(10, 20))
        title_label = tk.Label(title_frame, text="単語登録", font=('Arial', 18, 'bold'), bg='#099945', fg='white')
        title_label.pack(pady=5)

        # ===== 入力フォーム =====
        form = ttk.Frame(self.frame)
        form.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20)

        #単語名
        ttk.Label(self.frame, text="単語名：").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_Name.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        #リセットボタン
        ttk.Button(self.frame, text='リセット', command=self.controller.create_reset_window, style="Reset.TButton")\
           .grid(row=1, column=2, sticky="ne", padx=(0, 20), pady=5)
        
        # ふりがな
        ttk.Label(self.frame, text="ふりがな：").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_Yomi.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # 解説
        ttk.Label(self.frame, text="解説：").grid(row=4, column=0, sticky="ne", padx=10, pady=5)
        self.entry_Kai.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        # カテゴリ・タグ
        ttk.Label(self.frame, text="カテゴリ").grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.cb_Category.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self.frame, text="タグ").grid(row=6, column=0, sticky="e", padx=10, pady=5)
        self.cb_Tag.grid(row=6, column=1, sticky="w", padx=10, pady=5)


        # ===== ボタン行 =====
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text='単語一覧に戻る', command=self.controller.create_close_window, style="Back.TButton")\
            .grid(row=0, column=0, padx=10)

        ttk.Button(button_frame, text='作成', command=self.controller.get_id_pass, style="Create.TButton")\
            .grid(row=0, column=1, padx=10)

        # ===== grid の伸縮設定 =====
        self.frame.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Enter キー移動
        self.entry_Name.bind("<Return>", lambda e: self.entry_Yomi.focus_set())
        self.entry_Yomi.bind("<Return>", lambda e: self.entry_Kai.focus_set())

    def show(self):
        self.frame.pack(expand=True, fill='both')

    def close(self):
        self.frame.pack_forget()

    def set_combo_values(self, categories: list, tags: list):
        self.cb_Category['values'] = categories
        self.cb_Tag['values'] = tags

    def get_name(self):
        return self.entry_Name.get().strip()

    def get_yomi(self):
        return self.entry_Yomi.get().strip()

    def get_explain(self):
        return self.entry_Kai.get("1.0", "end-1c").strip()

    def get_category(self):
        return self.cb_Category.get().strip()

    def get_tag(self):
        return self.cb_Tag.get().strip()

    def _validate_hiragana(self, P):
        if P == "":
            return True
        import re
        return bool(re.fullmatch(r"[ぁ-ゖー]*", P))

    def clear_inputs(self):
        self.entry_Name.delete(0, tk.END)
        self.entry_Yomi.delete(0, tk.END)
        self.entry_Kai.delete("1.0", tk.END)
        self.cb_Category.set("")
        self.cb_Tag.set("")

    def show_error(self, msg: str):
        messagebox.showerror("エラー", msg)

    def show_success(self, msg: str):
        messagebox.showinfo("完了", msg)