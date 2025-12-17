import tkinter as tk
from tkinter import ttk
import re
from tkinter import messagebox

class WordbookView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("WordBook - Wordbook")
        self.controller = controller

        

        # UI状態
        self.name_is_visible = True
        self.desc_is_visible = True
        self.is_edit_mode = False
        
        # 生データを保持
        self.raw_name = ""
        self.raw_yomi = ""
        self.raw_description = ""
        self.raw_tag = ""
        self.raw_category = ""

        # Tk vars
        self.wordName_var = tk.StringVar(value="")
        self.wordYomi_var = tk.StringVar(value="") 
        self.btnName_var = tk.StringVar(value="名前を隠す")
        self.btnDescription_var = tk.StringVar(value="説明を隠す")
        self.category_var = tk.StringVar(value="")
        self.tag_var = tk.StringVar(value="")

        # 編集用変数
        self._edit_name_var = tk.StringVar(value="")
        self._edit_yomi_var = tk.StringVar(value="")
        self._edit_tag_var = tk.StringVar(value="")
        self._edit_category_var = tk.StringVar(value="")

        self._create_widgets()

    def _create_widgets(self):
        # メインコンテナ
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        vcmd = (self.register(self._validate_hiragana), "%P")

        main_frame.columnconfigure(1, weight=1)

        # === 1. ヘッダーエリア ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        ttk.Label(header_frame, text="単語詳細", font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        
        # 操作ボタン群コンテナ
        self.btn_frame_top = ttk.Frame(header_frame)
        self.btn_frame_top.pack(side=tk.RIGHT)
        
        # ボタン配置 (右から順に: 編集 -> 削除 -> (スペース) -> 説明隠す -> 名前隠す)
        # 修正: ボタン幅を広げて「キャンセル」が入るようにする
        self.edit_btn = ttk.Button(self.btn_frame_top, text="編集", command=self._on_edit_clicked, width=10)
        self.edit_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 修正: 削除ボタンは初期状態では無効化(編集モードでのみ有効)
        self.delete_btn = ttk.Button(self.btn_frame_top, text="削除", command=self.controller.handle_delete_word, width=10)
        self.delete_btn.config(state='disabled')
        self.delete_btn.pack(side=tk.RIGHT, padx=(15, 0)) 

        # 表示切替ボタン群
        self.visDescriptionBTN = ttk.Button(self.btn_frame_top, textvariable=self.btnDescription_var, command=self.controller.toggle_description_view, width=10)
        self.visDescriptionBTN.pack(side=tk.RIGHT, padx=(5, 0))

        self.visNameBTN = ttk.Button(self.btn_frame_top, textvariable=self.btnName_var, command=self.controller.toggle_name_view, width=10)
        self.visNameBTN.pack(side=tk.RIGHT, padx=(5, 0))

        # === 2. 単語名行 ===
        ttk.Label(main_frame, text="単語名 :", anchor='e').grid(row=1, column=0, sticky='ne', padx=5, pady=5)
        
        # 表示エリア
        self.name_display_frame = ttk.Frame(main_frame)
        self.name_display_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        self.label_name = ttk.Label(self.name_display_frame, textvariable=self.wordName_var, font=("TkDefaultFont", 16, "bold"), wraplength=450)
        self.label_name.pack(side=tk.LEFT, fill='x', expand=True)

        # 編集エリア (初期非表示)
        self.edit_name_entry = ttk.Entry(main_frame, textvariable=self._edit_name_var, font=("TkDefaultFont", 14))

        # === 3. 読み行 ===
        ttk.Label(main_frame, text="読み(ひらがな) :", anchor='e').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        
        self.label_yomi = ttk.Label(main_frame, textvariable=self.wordYomi_var)
        self.label_yomi.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        self.edit_yomi_entry = ttk.Entry(
            main_frame,
            textvariable=self._edit_yomi_var,
            validate="key",
            validatecommand=vcmd
        )

        # === 4. 説明文エリア ===
        desc_label_frame = ttk.Frame(main_frame)
        desc_label_frame.grid(row=3, column=0, sticky='ne', padx=5, pady=5)
        ttk.Label(desc_label_frame, text="説明 :").pack(anchor='e')
        
        # 説明エリア
        desc_content_frame = ttk.Frame(main_frame)
        desc_content_frame.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)
        main_frame.rowconfigure(3, weight=1) 

        # 表示用テキスト
        self.desc_text = tk.Text(desc_content_frame, wrap='word', height=8, width=40, bg="#f9f9f9", relief="flat")
        self.desc_text.config(state='disabled')
        self.desc_text.pack(fill='both', expand=True)

        # 編集用テキスト (初期非表示)
        self.edit_desc_text = tk.Text(desc_content_frame, wrap='word', height=8, width=40)

        # === 5. タグ・カテコリエリア ===
        # タグ
        ttk.Label(main_frame, text="タグ :", anchor='e').grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.label_tag = ttk.Label(main_frame, textvariable=self.tag_var)
        self.label_tag.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        self.edit_tag_combo = ttk.Combobox(main_frame, textvariable=self._edit_tag_var, state='normal')

        # カテゴリ
        ttk.Label(main_frame, text="カテゴリ :", anchor='e').grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.label_category = ttk.Label(main_frame, textvariable=self.category_var)
        self.label_category.grid(row=5, column=1, sticky='w', padx=5, pady=5)
        self.edit_category_combo = ttk.Combobox(main_frame, textvariable=self._edit_category_var, state='normal')

        # === 6. フッター (ナビゲーション & 保存) ===
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(20, 0))

        self.goListBTN = ttk.Button(footer_frame, text="< 戻る", command=self.controller.handle_go_word_list)
        self.goListBTN.pack(side=tk.LEFT)

        center_nav_frame = ttk.Frame(footer_frame)
        center_nav_frame.pack(side=tk.LEFT, expand=True)
        self.backPageBTN = ttk.Button(center_nav_frame, text="前のページへ", command=self.controller.handle_previous_word)
        self.backPageBTN.pack(side=tk.LEFT, padx=5)
        self.nextPageBTN = ttk.Button(center_nav_frame, text="次のページへ", command=self.controller.handle_next_word)
        self.nextPageBTN.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(footer_frame, text="変更を保存", command=self._on_save_clicked)

    def update_data(self, name, description, yomi: str = "", tag: str = None, category: str = None):
        self.raw_name = name or ""
        self.raw_yomi = yomi or ""
        self.raw_description = description or ""
        self.raw_tag = tag or ""
        self.raw_category = category or ""

        self._refresh_display()

        if self.is_edit_mode:
            self._enter_edit_widgets()

    def _refresh_display(self):
        """現在の表示モード（隠す/隠さない）に従って表示を更新"""
        # 名前と読み
        if self.name_is_visible:
            self.wordName_var.set(self.raw_name)
            self.wordYomi_var.set(self.raw_yomi) # 修正: 名前が見える時は読みも見せる
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.wordYomi_var.set("???") # 修正: 名前を隠すときは読みも隠す
            self.btnName_var.set("名前を見る")
        
        # 説明
        self.desc_text.config(state='normal')
        self.desc_text.delete("1.0", "end")
        if self.desc_is_visible:
            self.desc_text.insert("1.0", self.raw_description)
            self.btnDescription_var.set("説明を隠す")
        else:
            self.desc_text.insert("1.0", "???")
            self.btnDescription_var.set("説明を見る")
        self.desc_text.config(state='disabled')

        # タグ・カテゴリ
        self.category_var.set(self.raw_category or "未設定")
        disp_tag = self.raw_tag
        if disp_tag:
            cleaned = ", ".join([t.strip() for t in str(disp_tag).replace('、', ',').split(',') if t.strip()])
            disp_tag = cleaned
        self.tag_var.set(disp_tag or "未設定")

    # --- トグル操作 ---
    def toggle_name_display(self, is_visible):
        self.name_is_visible = is_visible
        self._refresh_display()

    def toggle_description_display(self, is_visible):
        self.desc_is_visible = is_visible
        self._refresh_display()

    # --- 編集モード制御 ---
    def _on_edit_clicked(self):
        if self.is_edit_mode:
            self.exit_edit_mode() # キャンセル
        else:
            self.is_edit_mode = True
            self.edit_btn.config(text="キャンセル")
            self._enter_edit_widgets()

    def exit_edit_mode(self):
        self.is_edit_mode = False
        self.edit_btn.config(text="単語を編集")
        self._exit_edit_widgets()

    def _enter_edit_widgets(self):
        # ナビゲーション等のボタンを無効化
        self._set_nav_buttons_state('disabled')

        # 修正: 削除ボタンを有効化
        self.delete_btn.config(state='normal')

        # コンボボックスの選択肢をロード
        try:
            cats = self.controller.get_available_categories()
            self.edit_category_combo['values'] = cats
            tags = self.controller.get_available_tags()
            self.edit_tag_combo['values'] = tags
        except Exception:
            pass

        # 値のセット (生データを使う)
        self._edit_name_var.set(self.raw_name)
        self._edit_yomi_var.set(self.raw_yomi)
        self._edit_tag_var.set(self.raw_tag)
        self._edit_category_var.set(self.raw_category)
        
        self.edit_desc_text.delete("1.0", "end")
        self.edit_desc_text.insert("1.0", self.raw_description)

        # 切り替え: 単語名
        self.name_display_frame.grid_remove()
        self.edit_name_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        # 修正: 単語名も編集可能にするため state='normal' (デフォルト) に戻す
        self.edit_name_entry.config(state='normal')

        # 切り替え: 読み
        self.label_yomi.grid_remove()
        self.edit_yomi_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        # 切り替え: 説明 (トグルボタンも隠す)
        self.visDescriptionBTN.pack_forget()
        self.desc_text.pack_forget()
        self.edit_desc_text.pack(fill='both', expand=True)

        # 切り替え: タグ
        self.label_tag.grid_remove()
        self.edit_tag_combo.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

        # 切り替え: カテゴリ
        self.label_category.grid_remove()
        self.edit_category_combo.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

        # 保存ボタン表示
        self.save_btn.pack(side=tk.RIGHT)

    def _exit_edit_widgets(self):
        # ボタン有効化（削除ボタン以外）
        self._set_nav_buttons_state('normal')
        
        # 修正: 削除ボタンを無効化
        self.delete_btn.config(state='disabled')

        # 単語名
        self.edit_name_entry.grid_remove()
        self.name_display_frame.grid()

        # 読み
        self.edit_yomi_entry.grid_remove()
        self.label_yomi.grid()

        # 説明
        self.edit_desc_text.pack_forget()
        self.visDescriptionBTN.pack(anchor='w', pady=(0, 5))
        self.desc_text.pack(fill='both', expand=True)

        # タグ
        self.edit_tag_combo.grid_remove()
        self.label_tag.grid()

        # カテゴリ
        self.edit_category_combo.grid_remove()
        self.label_category.grid()

        # 保存ボタン非表示
        self.save_btn.pack_forget()

    def _set_nav_buttons_state(self, state):
        # 削除ボタン以外のナビゲーション・表示ボタンを制御
        btns = [self.visNameBTN, self.visDescriptionBTN, self.backPageBTN, self.nextPageBTN, self.goListBTN]
        for btn in btns:
            btn.config(state=state)

    def _validate_hiragana(self, P):
        # P = 入力後の文字列
        if P == "":
            return True
        import re
        return bool(re.fullmatch(r"[ぁ-ゖー]*", P))

    def _on_save_clicked(self):
        
        name = self._edit_name_var.get().strip()
        yomi = self._edit_yomi_var.get().strip()
        tag = self._edit_tag_var.get().strip()
        category = self._edit_category_var.get().strip()
        desc = self.edit_desc_text.get("1.0", "end-1c").strip()

        #よみがな検証
        if not re.fullmatch(r"[ぁ-ゖー]*", yomi):
            messagebox.showerror("入力エラー", "読みはひらがなのみ入力してください")
            return

        self.controller.save_edits(name=name, description=desc, tag=tag, category=category, yomi=yomi)


    
        


        