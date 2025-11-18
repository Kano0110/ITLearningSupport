# View/Q_SelectView.py
import tkinter as tk
from tkinter import ttk, messagebox

class Q_SelectView:
    def __init__(self, root: tk.Tk, controller):
        self.controller = controller
        self.root = root
        self.frame = ttk.Frame(self.root, padding=0)
        self.tag_var = None
        self.category_var = None
        self._build_ui()

    def _build_ui(self):
        """UIを構築"""
        self._create_title()
        self._create_tag_selector()
        self._create_category_selector()
        self._create_buttons()
        self._create_back_button()

    def _create_title(self):
        """タイトルを作成"""
        title_frame = ttk.Frame(self.frame, padding=20)
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(title_frame, text="出題形式選択", font=('Arial', 20, 'bold'))
        title_label.pack()

    def _create_tag_selector(self):
        """タグセレクタを作成"""
        tag_frame = ttk.Frame(self.frame, padding=(20, 10))
        tag_frame.pack(fill='x')
        
        # ラベルとコンボボックスを配置するための内側フレーム
        inner_frame = ttk.Frame(tag_frame)
        inner_frame.pack(anchor='center')
        
        ttk.Label(inner_frame, text="タグ:").pack(side='left', padx=(0, 10))
        
        tags = self.controller.get_available_tags()
        self.tag_var = tk.StringVar(value='全て')
        tag_combo = ttk.Combobox(inner_frame, textvariable=self.tag_var, 
                                 values=['全て'] + tags, state='readonly', width=25)
        tag_combo.pack(side='left', padx=5)
        tag_combo.bind('<<ComboboxSelected>>', self.on_tag_selected)

    def _create_category_selector(self):
        """カテゴリセレクタを作成"""
        category_frame = ttk.Frame(self.frame, padding=(20, 10))
        category_frame.pack(fill='x')
        
        # ラベルとコンボボックスを配置するための内側フレーム
        inner_frame = ttk.Frame(category_frame)
        inner_frame.pack(anchor='center')
        
        ttk.Label(inner_frame, text="カテゴリ:").pack(side='left', padx=(0, 10))
        
        categories = self.controller.get_available_categories()
        self.category_var = tk.StringVar(value='全て')
        category_combo = ttk.Combobox(inner_frame, textvariable=self.category_var, 
                                      values=['全て'] + categories, state='readonly', width=25)
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.on_category_selected)

    def _create_buttons(self):
        """ボタンを作成（重要な選択肢）"""
        button_frame = ttk.Frame(self.frame, padding=20)
        button_frame.pack(fill='x', expand=True)
        
        # 内側フレーム（ボタンを中央に配置）
        inner_frame = ttk.Frame(button_frame)
        inner_frame.pack(anchor='center')
        
        # 「重要な順に出題」ボタン
        important_btn = ttk.Button(inner_frame, text="重要な順に出題", 
                                   command=self.on_important_quiz_click, width=20)
        important_btn.pack(side='left', padx=10, pady=20)
        
        # 「ランダムに出題」ボタン
        random_btn = ttk.Button(inner_frame, text="ランダムに出題", 
                               command=self.on_random_quiz_click, width=20)
        random_btn.pack(side='left', padx=10, pady=20)

    def _create_back_button(self):
        """戻るボタンを作成"""
        back_frame = ttk.Frame(self.frame, padding=(20, 10))
        back_frame.pack(fill='x')
        
        back_btn = ttk.Button(back_frame, text="＜戻る", command=self.on_back_click)
        back_btn.pack(anchor='w')

    def on_tag_selected(self, event):
        """タグが選択された時の処理"""
        tag_value = self.tag_var.get()
        if tag_value == '全て':
            self.controller.clear_tag()
        else:
            self.controller.select_tag(tag_value)

    def on_category_selected(self, event):
        """カテゴリが選択された時の処理"""
        category_value = self.category_var.get()
        if category_value == '全て':
            self.controller.clear_category()
        else:
            self.controller.select_category(category_value)

    def on_important_quiz_click(self):
        """重要な順に出題ボタンが押された時の処理"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        try:
            self.controller.app.start_quiz(terms, mode='important')
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("エラー", "問題を開始できませんでした")

    def on_random_quiz_click(self):
        """ランダムに出題ボタンが押された時の処理"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        try:
            self.controller.app.start_quiz(terms, mode='random')
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("エラー", "問題を開始できませんでした")

    def on_back_click(self):
        """戻るボタンが押された時の処理"""
        self.controller.go_to_home()

    def show(self):
        """表示処理"""
        self.frame.pack(expand=True, fill='both')
        try:
            self.root.update()
        except Exception:
            pass

    def hide(self):
        """非表示処理"""
        self.frame.pack_forget()
