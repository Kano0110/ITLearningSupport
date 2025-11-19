# WordbookView.py
import tkinter as tk
from tkinter import ttk

class WordbookView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("WordBook - Wordbook")
        self.controller = controller

        # UI状態
        self.name_is_visible = True
        self.desc_is_visible = True
        self.is_edit_mode = False

        # Tk vars
        self.wordName_var = tk.StringVar(value="")
        self.wordDescription_var = tk.StringVar(value="")  # used only for non-edit display
        self.btnName_var = tk.StringVar(value="名前を隠す")
        self.btnDescription_var = tk.StringVar(value="説明を隠す")
        self.category_var = tk.StringVar(value="")
        self.tag_var = tk.StringVar(value="")

        # 編集用変数（Entry/Text にバインド）
        self._edit_name_var = tk.StringVar(value="")
        self._edit_tag_var = tk.StringVar(value="")
        self._edit_category_var = tk.StringVar(value="")
        # description は Text widget を使うため StringVar は使わない

        self._create_widgets()

    def _create_widgets(self):
        outer = ttk.Frame(self)
        outer.pack(fill='both', expand=True, padx=12, pady=8)

        left_col = ttk.Frame(outer, width=160)
        left_col.pack(side=tk.LEFT, anchor='n', fill='y', padx=(0,12))

        right_col = ttk.Frame(outer)
        right_col.pack(side=tk.LEFT, fill='both', expand=True)

        # 編集ボタン（右上）
        top_row = ttk.Frame(right_col)
        top_row.pack(fill='x')
        self.edit_btn = ttk.Button(top_row, text="編集", command=self._on_edit_clicked)
        self.edit_btn.pack(side=tk.RIGHT, padx=4)

        # --- 左: メタ ---
        ttk.Label(left_col, text="カテゴリ", foreground='gray').pack(anchor='w', pady=(4,2))
        self.category_label = ttk.Label(left_col, textvariable=self.category_var, foreground='#333333', cursor='hand2')
        self.category_label.pack(anchor='w', pady=(0,8))
        self.category_label.bind("<Button-1>", self._on_category_click)

        ttk.Label(left_col, text="タグ", foreground='gray').pack(anchor='w', pady=(4,2))
        self.tag_label = ttk.Label(left_col, textvariable=self.tag_var, foreground='#333333', cursor='hand2')
        self.tag_label.pack(anchor='w', pady=(0,8))
        self.tag_label.bind("<Button-1>", self._on_tag_click)

        # --- 右: メイン表示 ---
        self.label1 = ttk.Label(right_col, textvariable=self.wordName_var, font=("TkDefaultFont", 14, "bold"), anchor='w')
        self.label1.pack(anchor='w', pady=(2,6))

        # トグルボタン群（名前/説明 の表示切替）
        btn_frame = ttk.Frame(right_col)
        btn_frame.pack(anchor='w', pady=(0,8))
        self.visNameBTN = ttk.Button(btn_frame, textvariable=self.btnName_var,
                                     command=self.controller.toggle_name_view)
        self.visDescriptionBTN = ttk.Button(btn_frame, textvariable=self.btnDescription_var,
                                            command=self.controller.toggle_description_view)
        self.visNameBTN.pack(side=tk.LEFT, padx=(0,6))
        self.visDescriptionBTN.pack(side=tk.LEFT)

        # 説明表示（通常は Text widget を read-only にして使う）
        self.desc_text = tk.Text(right_col, wrap='word', height=12, width=60)
        self.desc_text.config(state='disabled')
        self.desc_text.pack(fill='both', expand=True, pady=(8,8))

        # 編集用ウィジェット（最初は非表示）
        # 名前編集
        self.edit_name_entry = ttk.Entry(right_col, textvariable=self._edit_name_var, font=("TkDefaultFont", 12, "bold"))
        # 説明編集（Text）
        self.edit_desc_text = tk.Text(right_col, wrap='word', height=12, width=60)
        # タグ/カテゴリ編集（左カラムに表示する）
        self.edit_category_entry = ttk.Entry(left_col, textvariable=self._edit_category_var)
        self.edit_tag_entry = ttk.Entry(left_col, textvariable=self._edit_tag_var)

        # 編集時のアクションボタン（保存 / キャンセル）
        edit_action_frame = ttk.Frame(right_col)
        edit_action_frame.pack(fill='x', pady=(6,4))
        self.save_btn = ttk.Button(edit_action_frame, text="変更する", command=self._on_save_clicked)
        # 最初は表示しない
        self.save_btn.pack_forget()

        # ナビゲーションボタン
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
        """表示モードに合わせてデータを反映する（編集モードでなければ通常表示）"""
        # 常に保存される変数も更新（編集開始時の初期値にするため）
        self._edit_name_var.set(name or "")
        self._edit_tag_var.set(tag or "")
        self._edit_category_var.set(category or "")
        # name
        if self.name_is_visible:
            self.wordName_var.set(name or "")
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")
        # description
        self.desc_text.config(state='normal')
        self.desc_text.delete("1.0", "end")
        if self.desc_is_visible:
            self.desc_text.insert("1.0", description or "")
            self.btnDescription_var.set("説明を隠す")
        else:
            self.desc_text.insert("1.0", "???")
            self.btnDescription_var.set("説明を見る")
        self.desc_text.config(state='disabled')
        # meta
        self.category_var.set(category or "未設定")
        # tag: display formatted
        if tag:
            cleaned = ", ".join([t.strip() for t in str(tag).replace('、', ',').split(',') if t.strip()])
            self.tag_var.set(cleaned)
        else:
            self.tag_var.set("未設定")

        # 編集モード時は編集ウィジェットに現在値を流す
        if self.is_edit_mode:
            # show edit widgets
            self._enter_edit_widgets()

    # --- 編集モード制御 (View側UI操作) ---
    def _on_edit_clicked(self):
        if self.is_edit_mode:
            # 編集中にもう一度押された → キャンセル扱い
            self._exit_edit_widgets()
            if hasattr(self.controller, "cancel_edits"):
                try:
                    self.controller.cancel_edits()
                except Exception:
                    pass
            return

        # 編集モード開始
        self.is_edit_mode = True
        self.edit_btn.config(text="キャンセル")  # 編集中は「キャンセル」と表示
        self._enter_edit_widgets()

    def _enter_edit_widgets(self):
        """表示 -> 編集用ウィジェットに切り替え（既に is_edit_mode True の前提）"""
        # 左カラム: 文字列ラベルを entry に置換して pack
        # category / tag: hide labels, show entries
        try:
            self.category_label.pack_forget()
            self.tag_label.pack_forget()
        except Exception:
            pass
        # place edit entries at same position
        self.edit_category_entry.pack(anchor='w', pady=(0,8))
        self.edit_tag_entry.pack(anchor='w', pady=(0,8))

        # 右カラム: name label -> entry
        try:
            self.label1.pack_forget()
        except Exception:
            pass
        self.edit_name_entry.pack(anchor='w', pady=(2,6), fill='x')
        # description: show editable text
        self.desc_text.pack_forget()
        self.edit_desc_text.pack(fill='both', expand=True, pady=(8,8))
        # prefill edit_desc_text
        self.edit_desc_text.delete("1.0", "end")
        self.edit_desc_text.insert("1.0", self.desc_text.get("1.0", "end").rstrip("\n"))
        # show Save/Cancel
        self.save_btn.pack(side=tk.RIGHT, padx=6)

    def _exit_edit_widgets(self):
        """編集ウィジェットを閉じて通常表示に戻す"""
        # hide edit widgets
        try:
            self.edit_category_entry.pack_forget()
            self.edit_tag_entry.pack_forget()
        except Exception:
            pass
        try:
            self.edit_name_entry.pack_forget()
            self.edit_desc_text.pack_forget()
        except Exception:
            pass
        # restore labels
        self.category_label.pack(anchor='w', pady=(0,8))
        self.tag_label.pack(anchor='w', pady=(0,8))
        self.label1.pack(anchor='w', pady=(2,6))
        self.desc_text.pack(fill='both', expand=True, pady=(8,8))
        # hide Save/Cancel
        self.save_btn.pack_forget()
        # restore edit button label
        self.edit_btn.config(text="編集")
        self.is_edit_mode = False

    def _on_save_clicked(self):
        """保存ボタン押下: View の編集値を取り出して Controller に渡す"""
        name = self._edit_name_var.get().strip()
        tag = self._edit_tag_var.get().strip()
        category = self._edit_category_var.get().strip()
        desc = self.edit_desc_text.get("1.0", "end").rstrip("\n")
        # delegate save to controller (controller は成功時に view を更新してくれる想定)
        self.controller.save_edits(name=name, description=desc, tag=tag, category=category)

    # --- toggle display (used by controller) ---
    def toggle_name_display(self, is_visible, name):
        self.name_is_visible = is_visible
        if is_visible:
            self.wordName_var.set(name)
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")

    def toggle_description_display(self, is_visible, description):
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