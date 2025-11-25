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
        self.wordDescription_var = tk.StringVar(value="")
        self.btnName_var = tk.StringVar(value="名前を隠す")
        self.btnDescription_var = tk.StringVar(value="説明を隠す")
        self.category_var = tk.StringVar(value="")
        self.tag_var = tk.StringVar(value="")
        self.wordYomi_var = tk.StringVar(value="") 

        # 編集用変数
        self._edit_name_var = tk.StringVar(value="")
        self._edit_tag_var = tk.StringVar(value="")
        self._edit_category_var = tk.StringVar(value="")
        self._edit_yomi_var = tk.StringVar(value="") 

        self._create_widgets()

    def _create_widgets(self):
        outer = ttk.Frame(self)
        outer.pack(fill='both', expand=True, padx=12, pady=8)

        left_col = ttk.Frame(outer, width=160)
        left_col.pack(side=tk.LEFT, anchor='n', fill='y', padx=(0,12))

        right_col = ttk.Frame(outer)
        right_col.pack(side=tk.LEFT, fill='both', expand=True)

        # 右上: 操作ボタンエリア
        top_row = ttk.Frame(right_col)
        top_row.pack(fill='x')
        
        self.edit_btn = ttk.Button(top_row, text="編集", command=self._on_edit_clicked)
        self.edit_btn.pack(side=tk.RIGHT, padx=4)
        
        self.delete_btn = ttk.Button(top_row, text="削除", command=self.controller.handle_delete_word)
        self.delete_btn.pack(side=tk.RIGHT, padx=4)

        # --- 左カラム (メタ情報) ---
        self.cat_container = ttk.Frame(left_col)
        self.cat_container.pack(anchor='w', pady=(4,2), fill='x')
        ttk.Label(self.cat_container, text="カテゴリ", foreground='gray').pack(anchor='w')
        self.category_label = ttk.Label(self.cat_container, textvariable=self.category_var, foreground='#333333', cursor='hand2')
        self.category_label.pack(anchor='w', pady=(0,8))
        self.category_label.bind("<Button-1>", self._on_category_click)
        self.edit_category_entry = ttk.Entry(self.cat_container, textvariable=self._edit_category_var)

        self.tag_container = ttk.Frame(left_col)
        self.tag_container.pack(anchor='w', pady=(4,2), fill='x')
        ttk.Label(self.tag_container, text="タグ", foreground='gray').pack(anchor='w')
        self.tag_label = ttk.Label(self.tag_container, textvariable=self.tag_var, foreground='#333333', cursor='hand2')
        self.tag_label.pack(anchor='w', pady=(0,8))
        self.tag_label.bind("<Button-1>", self._on_tag_click)
        self.edit_tag_entry = ttk.Entry(self.tag_container, textvariable=self._edit_tag_var)

        # --- 右カラム (メイン表示) ---
        self.name_container = ttk.Frame(right_col)
        self.name_container.pack(fill='x', pady=(2,6))
        self.label1 = ttk.Label(self.name_container, textvariable=self.wordName_var, font=("TkDefaultFont", 14, "bold"), anchor='w')
        self.label1.pack(anchor='w', fill='x')
        self.edit_name_entry = ttk.Entry(self.name_container, textvariable=self._edit_name_var, font=("TkDefaultFont", 12, "bold"))
        self.edit_name_entry.config(state='readonly') 

        self.yomi_container = ttk.Frame(right_col)
        self.yomi_container.pack(fill='x', pady=(0,6))
        self.label_yomi = ttk.Label(self.yomi_container, textvariable=self.wordYomi_var, font=("TkDefaultFont", 10), anchor='w', foreground="#555555")
        self.label_yomi.pack(anchor='w', fill='x')
        self.edit_yomi_entry = ttk.Entry(self.yomi_container, textvariable=self._edit_yomi_var)

        btn_frame = ttk.Frame(right_col)
        btn_frame.pack(anchor='w', pady=(0,8))
        self.visNameBTN = ttk.Button(btn_frame, textvariable=self.btnName_var, command=self.controller.toggle_name_view)
        self.visDescriptionBTN = ttk.Button(btn_frame, textvariable=self.btnDescription_var, command=self.controller.toggle_description_view)
        self.visNameBTN.pack(side=tk.LEFT, padx=(0,6))
        self.visDescriptionBTN.pack(side=tk.LEFT)

        self.desc_container = ttk.Frame(right_col)
        self.desc_container.pack(fill='both', expand=True, pady=(8,8))
        self.desc_text = tk.Text(self.desc_container, wrap='word', height=12, width=60)
        self.desc_text.config(state='disabled')
        self.desc_text.pack(fill='both', expand=True)
        self.edit_desc_text = tk.Text(self.desc_container, wrap='word', height=12, width=60)

        self.edit_action_frame = ttk.Frame(right_col)
        self.edit_action_frame.pack(fill='x', pady=(6,4))
        self.save_btn = ttk.Button(self.edit_action_frame, text="変更する", command=self._on_save_clicked)

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

    def update_data(self, name, description, yomi: str = "", tag: str = None, category: str = None):
        self._edit_name_var.set(name or "")
        self._edit_yomi_var.set(yomi or "")
        self._edit_tag_var.set(tag or "")
        self._edit_category_var.set(category or "")
        
        if self.name_is_visible:
            self.wordName_var.set(name or "")
            self.wordYomi_var.set(yomi or "")
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.wordYomi_var.set("???")
            self.btnName_var.set("名前を見る")
            
        #self.wordYomi_var.set(yomi or "")

        self.desc_text.config(state='normal')
        self.desc_text.delete("1.0", "end")
        if self.desc_is_visible:
            self.desc_text.insert("1.0", description or "")
            self.btnDescription_var.set("説明を隠す")
        else:
            self.desc_text.insert("1.0", "???")
            self.btnDescription_var.set("説明を見る")
        self.desc_text.config(state='disabled')
        
        self.category_var.set(category or "未設定")
        if tag:
            cleaned = ", ".join([t.strip() for t in str(tag).replace('、', ',').split(',') if t.strip()])
            self.tag_var.set(cleaned)
        else:
            self.tag_var.set("未設定")

        if self.is_edit_mode:
            self._enter_edit_widgets()

    def _on_edit_clicked(self):
        if self.is_edit_mode:
            self._exit_edit_widgets()
            if hasattr(self.controller, "cancel_edits"):
                try:
                    self.controller.cancel_edits()
                except Exception:
                    pass
            return
        self.is_edit_mode = True
        self.edit_btn.config(text="キャンセル")
        self._enter_edit_widgets()

    def exit_edit_mode(self):
        self._exit_edit_widgets()

    def _enter_edit_widgets(self):
        # ボタン無効化
        for btn in [self.visNameBTN, self.visDescriptionBTN, self.backPageBTN, self.nextPageBTN, self.goHomeBTN, self.goListBTN, self.delete_btn]:
            btn.config(state='disabled')

        # 表示切替
        self.category_label.pack_forget()
        self.edit_category_entry.pack(anchor='w', pady=(0,8), fill='x')
        
        self.tag_label.pack_forget()
        self.edit_tag_entry.pack(anchor='w', pady=(0,8), fill='x')
        
        self.label1.pack_forget()
        self.edit_name_entry.pack(anchor='w', fill='x')
        
        self.label_yomi.pack_forget()
        self.edit_yomi_entry.pack(anchor='w', fill='x')
        
        self.desc_text.pack_forget()
        self.edit_desc_text.pack(fill='both', expand=True)
        self.edit_desc_text.delete("1.0", "end")
        self.edit_desc_text.insert("1.0", self.desc_text.get("1.0", "end").rstrip("\n"))
        
        self.save_btn.pack(side=tk.RIGHT, padx=6)

    def _exit_edit_widgets(self):
        # ボタン有効化
        for btn in [self.visNameBTN, self.visDescriptionBTN, self.backPageBTN, self.nextPageBTN, self.goHomeBTN, self.goListBTN, self.delete_btn]:
            btn.config(state='normal')

        # 表示切替戻し
        self.edit_category_entry.pack_forget()
        self.category_label.pack(anchor='w', pady=(0,8))
        
        self.edit_tag_entry.pack_forget()
        self.tag_label.pack(anchor='w', pady=(0,8))
        
        self.edit_name_entry.pack_forget()
        self.label1.pack(anchor='w', fill='x')
        
        self.edit_yomi_entry.pack_forget()
        self.label_yomi.pack(anchor='w', fill='x')
        
        self.edit_desc_text.pack_forget()
        self.desc_text.pack(fill='both', expand=True)
        
        self.save_btn.pack_forget()
        self.edit_btn.config(text="編集")
        self.is_edit_mode = False

    def _on_save_clicked(self):
        name = self._edit_name_var.get().strip()
        yomi = self._edit_yomi_var.get().strip()
        tag = self._edit_tag_var.get().strip()
        category = self._edit_category_var.get().strip()
        desc = self.edit_desc_text.get("1.0", "end").rstrip("\n")
        self.controller.save_edits(name=name, description=desc, tag=tag, category=category, yomi=yomi)

    def toggle_name_display(self, is_visible, name, yomi):
        self.name_is_visible = is_visible
        if is_visible:
            self.wordName_var.set(name)
            self.wordYomi_var.set(yomi)
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.wordYomi_var.set("???")
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

    def _on_category_click(self, event=None):
        pass

    def _on_tag_click(self, event=None):
        pass