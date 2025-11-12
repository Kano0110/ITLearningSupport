# WordbookView.py
import tkinter as tk
from tkinter import ttk

class WordbookView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("WordBookPage")
        self.controller = controller

        # UI状態を管理するインスタンス変数 (Viewの責務)
        self.name_is_visible = True
        self.desc_is_visible = True

        # Tkinter変数 (StringVar) の定義
        self.wordName_var = tk.StringVar(value="")
        self.wordDescription_var = tk.StringVar(value="")
        self.btnName_var = tk.StringVar(value="名前を隠す")
        self.btnDescription_var = tk.StringVar(value="説明を隠す")

        # メタ（カテゴリ・タグ）用変数
        self.category_var = tk.StringVar(value="")
        self.tag_var = tk.StringVar(value="")

        self._create_widgets()

    def _create_widgets(self):
        # レイアウト: 左にメタ、右に本文という2カラム構成にする
        outer = ttk.Frame(self)
        outer.pack(fill='both', expand=True, padx=12, pady=8)

        left_col = ttk.Frame(outer, width=160)
        left_col.pack(side=tk.LEFT, anchor='n', fill='y', padx=(0,12))

        right_col = ttk.Frame(outer)
        right_col.pack(side=tk.LEFT, fill='both', expand=True)

        # --- 左: カテゴリ・タグ領域（小さめ・左寄せ・控えめ表示） ---
        ttk.Label(left_col, text="カテゴリ", foreground='gray').pack(anchor='w', pady=(4,2))
        self.category_label = ttk.Label(left_col, textvariable=self.category_var, foreground='#333333', cursor='hand2')
        self.category_label.pack(anchor='w', pady=(0,8))
        self.category_label.bind("<Button-1>", self._on_category_click)

        ttk.Label(left_col, text="タグ", foreground='gray').pack(anchor='w', pady=(4,2))
        self.tag_label = ttk.Label(left_col, textvariable=self.tag_var, foreground='#333333', cursor='hand2')
        self.tag_label.pack(anchor='w', pady=(0,8))
        self.tag_label.bind("<Button-1>", self._on_tag_click)

        # --- 右: メイン表示（名前・説明・トグル・操作） ---
        self.label1 = ttk.Label(right_col, textvariable=self.wordName_var, font=("TkDefaultFont", 14, "bold"), anchor='w')
        self.label1.pack(anchor='w', pady=(2,6))

        # 表示/非表示トグルボタンを横並びで配置
        btn_frame = ttk.Frame(right_col)
        btn_frame.pack(anchor='w', pady=(0,8))
        self.visNameBTN = ttk.Button(btn_frame, textvariable=self.btnName_var,
                                     command=self.controller.toggle_name_view)
        self.visDescriptionBTN = ttk.Button(btn_frame, textvariable=self.btnDescription_var,
                                            command=self.controller.toggle_description_view)
        self.visNameBTN.pack(side=tk.LEFT, padx=(0,6))
        self.visDescriptionBTN.pack(side=tk.LEFT)

        # 説明は Text にして長文対応（wrap）
        self.desc_text = tk.Text(right_col, wrap='word', height=12, width=60)
        self.desc_text.config(state='disabled')
        self.desc_text.pack(fill='both', expand=True, pady=(8,8))

        # ナビゲーションボタン群
        nav_frame = ttk.Frame(right_col)
        nav_frame.pack(fill='x', pady=(6,0))
        self.backPageBTN = ttk.Button(nav_frame, text="前のページへ", command=self.controller.handle_previous_word)
        self.nextPageBTN = ttk.Button(nav_frame, text="次のページへ", command=self.controller.handle_next_word)
        self.goHomeBTN = ttk.Button(nav_frame, text="homeへ戻る", command=self.controller.handle_go_home)
        self.goListBTN = ttk.Button(nav_frame, text="単語一覧へ戻る", command=self.controller.handle_go_word_list)

        self.backPageBTN.pack(side=tk.LEFT, padx=6)
        self.nextPageBTN.pack(side=tk.LEFT, padx=6)
        self.goHomeBTN.pack(side=tk.RIGHT, padx=6)
        self.goListBTN.pack(side=tk.RIGHT, padx=6)

    # --- Controllerから呼び出されるメソッド ---
    def update_data(self, name, description, tag: str = None, category: str = None):
        """常に現在の単語に合わせて更新。tag/category が None なら未設定扱いにする"""
        # 名前
        if self.name_is_visible:
            self.wordName_var.set(name or "")
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")

        # 説明（Text）
        self.desc_text.config(state='normal')
        self.desc_text.delete("1.0", "end")
        if self.desc_is_visible:
            self.desc_text.insert("1.0", description or "")
            self.btnDescription_var.set("説明を隠す")
        else:
            self.desc_text.insert("1.0", "???")
            self.btnDescription_var.set("説明を見る")
        self.desc_text.config(state='disabled')

        # カテゴリ（常に上書き、空は「未設定」）
        if category is None or str(category).strip() == "":
            self.category_var.set("未設定")
        else:
            self.category_var.set(str(category).strip())

        # タグ（常に上書き、空は「未設定」）。全角読点を半角に揃え、揃えて表示
        if tag is None or str(tag).strip() == "":
            self.tag_var.set("未設定")
        else:
            cleaned = ", ".join([t.strip() for t in str(tag).replace('、', ',').split(',') if t.strip()])
            self.tag_var.set(cleaned)

    def toggle_name_display(self, is_visible, name):
        """Controllerから呼ばれる (保持している name を渡して表示切替)"""
        self.name_is_visible = is_visible
        if is_visible:
            self.wordName_var.set(name)
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")

    def toggle_description_display(self, is_visible, description):
        """Controllerから呼ばれる"""
        self.desc_is_visible = is_visible
        self.desc_text.config(state='normal')
        if is_visible:
            self.desc_text.delete("1.0", "end")
            self.desc_text.insert("1.0", description or "")
            self.btnDescription_var.set("説明を隠す")
        else:
            self.desc_text.delete("1.0", "end")
            self.desc_text.insert("1.0", "???")
            self.btnDescription_var.set("説明を見る")
        self.desc_text.config(state='disabled')

    # --- メタクリックハンドラ（将来の検索遷移用） ---
    def _on_category_click(self, event=None):
        """カテゴリラベルがクリックされたときに controller の search_by_category を呼ぶ（存在すれば）"""
        try:
            val = self.category_var.get() if hasattr(self, "category_var") and hasattr(self.category_var, "get") else ""
            if not val or val == "未設定":
                return
            if hasattr(self.controller, "search_by_category"):
                try:
                    self.controller.search_by_category(val)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_tag_click(self, event=None):
        """タグラベルがクリックされたときに controller の search_by_tag を呼ぶ（存在すれば）"""
        try:
            val = self.tag_var.get() if hasattr(self, "tag_var") and hasattr(self.tag_var, "get") else ""
            if not val or val == "未設定":
                return
            if hasattr(self.controller, "search_by_tag"):
                try:
                    self.controller.search_by_tag(val)
                except Exception:
                    pass
        except Exception:
            pass