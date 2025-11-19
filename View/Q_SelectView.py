# View/Q_SelectView.py
import tkinter as tk
from tkinter import ttk, messagebox

class Q_SelectView:
    """出題形式選択画面の View
    
    責務：UI 表示のみ。ビジネスロジックは一切含まない。
    """

    def __init__(self, root: tk.Tk, controller):
        """初期化
        
        Args:
            root: Tk ルートウィンドウ
            controller: Q_SelectController インスタンス
        """
        self.controller = controller
        self.root = root
        self.frame = ttk.Frame(self.root, padding=0)
        
        # UI 要素への参照
        self.tag_combo = None
        self.category_combo = None
        self.summary_label = None
        
        # UI を構築
        self._build_ui()
        
        # Controller にコールバックを登録
        self.controller.set_view_update_callback(self._on_state_changed)

    def _build_ui(self):
        """UI を構築"""
        self._create_title()
        self._create_selectors()
        self._create_buttons()
        self._create_back_button()

    def _create_title(self):
        """タイトルエリアを作成"""
        title_frame = ttk.Frame(self.frame, padding=20)
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(
            title_frame,
            text="出題形式選択",
            font=('Arial', 18, 'bold')
        )
        title_label.pack()

    def _create_selectors(self):
        """タグ・カテゴリセレクタを作成"""
        selectors_frame = ttk.Frame(self.frame, padding=(20, 20, 20, 10))
        selectors_frame.pack(fill='x')

        # タグセレクタ
        tag_frame = ttk.Frame(selectors_frame)
        tag_frame.pack(fill='x', pady=10)
        
        ttk.Label(tag_frame, text="タグ:", font=('Arial', 11)).pack(side='left', padx=(0, 10))
        
        tags = self.controller.get_available_tags()
        self.tag_combo = ttk.Combobox(
            tag_frame,
            values=['全て'] + tags,
            state='readonly',
            width=30,
            font=('Arial', 11)
        )
        self.tag_combo.set('全て')
        self.tag_combo.pack(side='left', fill='x', expand=True)
        self.tag_combo.bind('<<ComboboxSelected>>', self._on_tag_changed)

        # カテゴリセレクタ
        category_frame = ttk.Frame(selectors_frame)
        category_frame.pack(fill='x', pady=10)
        
        ttk.Label(category_frame, text="カテゴリ:", font=('Arial', 11)).pack(side='left', padx=(0, 10))
        
        categories = self.controller.get_available_categories()
        self.category_combo = ttk.Combobox(
            category_frame,
            values=['全て'] + categories,
            state='readonly',
            width=30,
            font=('Arial', 11)
        )
        self.category_combo.set('全て')
        self.category_combo.pack(side='left', fill='x', expand=True)
        self.category_combo.bind('<<ComboboxSelected>>', self._on_category_changed)

        # 選択サマリー
        summary_frame = ttk.Frame(selectors_frame)
        summary_frame.pack(fill='x', pady=(20, 0))
        
        self.summary_label = ttk.Label(
            summary_frame,
            text="全て (0個)",
            font=('Arial', 10),
            foreground='gray'
        )
        self.summary_label.pack(side='left')

    def _create_buttons(self):
        """出題ボタンを作成"""
        buttons_frame = ttk.Frame(self.frame, padding=(20, 30, 20, 20))
        buttons_frame.pack(fill='both', expand=True)

        # 中央に配置するための内側フレーム
        inner_buttons_frame = ttk.Frame(buttons_frame)
        inner_buttons_frame.pack(expand=True)

        # 「重要な順に出題」ボタン
        important_btn = ttk.Button(
            inner_buttons_frame,
            text="重要な順に出題",
            command=self._on_important_btn_click,
            width=20
        )
        important_btn.pack(side='left', padx=20, pady=20)

        # 「ランダムに出題」ボタン
        random_btn = ttk.Button(
            inner_buttons_frame,
            text="ランダムに出題",
            command=self._on_random_btn_click,
            width=20
        )
        random_btn.pack(side='left', padx=20, pady=20)

    def _create_back_button(self):
        """戻るボタンを作成"""
        back_frame = ttk.Frame(self.frame, padding=(20, 10, 20, 20))
        back_frame.pack(fill='x')

        back_btn = ttk.Button(
            back_frame,
            text="＜戻る",
            command=self._on_back_btn_click,
            width=15
        )
        back_btn.pack(anchor='w')

    def _on_tag_changed(self, event):
        """タグコンボボックスが変更された"""
        tag_value = self.tag_combo.get()
        if tag_value == '全て':
            self.controller.clear_tag()
        else:
            self.controller.select_tag(tag_value)

    def _on_category_changed(self, event):
        """カテゴリコンボボックスが変更された"""
        category_value = self.category_combo.get()
        if category_value == '全て':
            self.controller.clear_category()
        else:
            self.controller.select_category(category_value)

    def _on_state_changed(self, tag_display: str, category_display: str):
        """Controller から状態更新通知を受け取る
        
        Args:
            tag_display: 表示するタグ（"全て" または タグ名）
            category_display: 表示するカテゴリ（"全て" または カテゴリ名）
        """
        # コンボボックスを更新
        self.tag_combo.set(tag_display)
        self.category_combo.set(category_display)
        
        # サマリーを更新
        summary = self.controller.get_selection_summary()
        self.summary_label.config(text=summary)

    def _on_important_btn_click(self):
        """「重要な順に出題」ボタンがクリックされた"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_important_order()

    def _on_random_btn_click(self):
        """「ランダムに出題」ボタンがクリックされた"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_random()

    def _on_back_btn_click(self):
        """戻るボタンがクリックされた"""
        self.controller.go_to_home()

    def show(self):
        """View を表示（AppController から呼ばれる）"""
        self.frame.pack(expand=True, fill='both')
        try:
            self.root.update()
        except Exception:
            pass

    def hide(self):
        """View を非表示（AppController から呼ばれる）"""
        self.frame.pack_forget()

    