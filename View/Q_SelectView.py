# View/Q_SelectView.py
import tkinter as tk
from tkinter import ttk, messagebox

class Q_SelectView:
    """出題形式選択画面の View (タグ/カテゴリ マルチ選択対応)
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
        self.tag_vars: dict[str, tk.BooleanVar] = {}
        self.category_vars: dict[str, tk.BooleanVar] = {}
        self.summary_label = None
        self.tags_container = None
        self.categories_container = None
        
        # UI を構築
        self._build_ui()
        
        # Controller にコールバックを登録
        self.controller.set_view_update_callback(self._on_state_changed)

    def _build_ui(self):
        """UI を構築"""
        self._create_title()
        self._create_multi_selectors()
        self._create_quiz_buttons()
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

    def _create_multi_selectors(self):
        """タグ/カテゴリのチェックボックス群を作成（スクロール対応）"""
        outer = ttk.Frame(self.frame, padding=(20, 20, 20, 10))
        outer.pack(fill='both', expand=False)

        # タグ領域（スクロール対応）
        tags_frame = ttk.LabelFrame(outer, text="タグ", padding=10)
        tags_frame.pack(fill='x', pady=(0, 10))
        
        # タグ用キャンバスとスクロールバー（2行分の高さ）
        tags_canvas = tk.Canvas(tags_frame, height=50)
        tags_scrollbar = ttk.Scrollbar(tags_frame, orient='vertical', command=tags_canvas.yview)
        tags_canvas.configure(yscrollcommand=tags_scrollbar.set)
        
        self.tags_container = ttk.Frame(tags_canvas)
        tags_canvas_window = tags_canvas.create_window((0, 0), window=self.tags_container, anchor='nw')
        
        tags_canvas.pack(side='left', fill='both', expand=True)
        tags_scrollbar.pack(side='right', fill='y')
        
        # タグコンテナのサイズ変更時にスクロール領域を更新
        self.tags_container.bind("<Configure>", lambda e: tags_canvas.configure(scrollregion=tags_canvas.bbox("all")))
        tags_canvas.bind("<Configure>", lambda e: tags_canvas.itemconfig(tags_canvas_window, width=e.width))
        
        self._build_tag_checkboxes()

        # カテゴリ領域（スクロール対応）
        categories_frame = ttk.LabelFrame(outer, text="カテゴリ", padding=10)
        categories_frame.pack(fill='x', pady=(0, 10))
        
        # カテゴリ用キャンバスとスクロールバー（2行分の高さ）
        categories_canvas = tk.Canvas(categories_frame, height=45)
        categories_scrollbar = ttk.Scrollbar(categories_frame, orient='vertical', command=categories_canvas.yview)
        categories_canvas.configure(yscrollcommand=categories_scrollbar.set)
        
        self.categories_container = ttk.Frame(categories_canvas)
        categories_canvas_window = categories_canvas.create_window((0, 0), window=self.categories_container, anchor='nw')
        
        categories_canvas.pack(side='left', fill='both', expand=True)
        categories_scrollbar.pack(side='right', fill='y')
        
        # カテゴリコンテナのサイズ変更時にスクロール領域を更新
        self.categories_container.bind("<Configure>", lambda e: categories_canvas.configure(scrollregion=categories_canvas.bbox("all")))
        categories_canvas.bind("<Configure>", lambda e: categories_canvas.itemconfig(categories_canvas_window, width=e.width))
        
        self._build_category_checkboxes()

        # 操作ボタン行（全解除 / 更新）
        ops_frame = ttk.Frame(outer)
        ops_frame.pack(fill='x', pady=(5, 5))
        clear_btn = ttk.Button(ops_frame, text="全て解除", command=self._on_clear_all_click, width=12)
        clear_btn.pack(side='left', padx=(0, 10))
        select_all_tags_btn = ttk.Button(ops_frame, text="タグ全選択", command=self._on_select_all_tags_click, width=12)
        select_all_tags_btn.pack(side='left', padx=(0, 10))
        select_all_categories_btn = ttk.Button(ops_frame, text="カテゴリ全選択", command=self._on_select_all_categories_click, width=14)
        select_all_categories_btn.pack(side='left', padx=(0, 10))

        # サマリー表示
        summary_frame = ttk.Frame(outer)
        summary_frame.pack(fill='x', pady=(10, 0))
        self.summary_label = ttk.Label(summary_frame, text="全て (0個)", font=('Arial', 10), foreground='gray')
        self.summary_label.pack(side='left')

    def _build_tag_checkboxes(self):
        for widget in self.tags_container.winfo_children():
            widget.destroy()
        tags = self.controller.get_available_tags()
        if not tags:
            ttk.Label(self.tags_container, text="タグなし", foreground='gray').pack(anchor='w')
            return
        # 横並び自動折り返し（2行表示）
        row_frame = ttk.Frame(self.tags_container)
        row_frame.pack(fill='x', anchor='w')
        col_count = 0
        MAX_COLS = 8  # 1行あたりの最大チェックボックス数
        for tag in tags:
            var = self.tag_vars.get(tag) or tk.BooleanVar(value=False)
            self.tag_vars[tag] = var
            cb = ttk.Checkbutton(row_frame, text=tag, variable=var, command=lambda t=tag: self._on_tag_toggle(t))
            cb.pack(side='left', padx=4, pady=2)
            col_count += 1
            if col_count >= MAX_COLS:
                row_frame = ttk.Frame(self.tags_container)
                row_frame.pack(fill='x', anchor='w')
                col_count = 0

    def _build_category_checkboxes(self):
        for widget in self.categories_container.winfo_children():
            widget.destroy()
        categories = self.controller.get_available_categories()
        if not categories:
            ttk.Label(self.categories_container, text="カテゴリなし", foreground='gray').pack(anchor='w')
            return
        # 横並び自動折り返し（2行表示）
        row_frame = ttk.Frame(self.categories_container)
        row_frame.pack(fill='x', anchor='w')
        col_count = 0
        MAX_COLS = 8  # 1行あたりの最大チェックボックス数
        for cat in categories:
            var = self.category_vars.get(cat) or tk.BooleanVar(value=False)
            self.category_vars[cat] = var
            cb = ttk.Checkbutton(row_frame, text=cat, variable=var, command=lambda c=cat: self._on_category_toggle(c))
            cb.pack(side='left', padx=4, pady=2)
            col_count += 1
            if col_count >= MAX_COLS:
                row_frame = ttk.Frame(self.categories_container)
                row_frame.pack(fill='x', anchor='w')
                col_count = 0

    def _create_quiz_buttons(self):
        """出題ボタンを作成"""
        buttons_frame = ttk.Frame(self.frame, padding=(20, 0, 20, 10))
        buttons_frame.pack(fill='both', expand=True)

        # 中央に配置するための内側フレーム
        inner_buttons_frame = ttk.Frame(buttons_frame)
        inner_buttons_frame.pack(expand=True)

        # 「単語を隠して出題」ボタン
        hide_words_btn = ttk.Button(
            inner_buttons_frame,
            text="単語を隠して出題",
            command=self._on_hide_words_click,
            width=20
        )
        hide_words_btn.pack(side='left', padx=20, pady=20)

        # 「説明を隠して出題」ボタン
        hide_explanations_btn = ttk.Button(
            inner_buttons_frame,
            text="説明を隠して出題",
            command=self._on_hide_explanations_click,
            width=20
        )
        hide_explanations_btn.pack(side='left', padx=20, pady=20)

    def _create_back_button(self):
        """戻るボタンを作成"""
        back_frame = ttk.Frame(self.frame, padding=(20, 5, 20, 10))
        back_frame.pack(fill='x')

        back_btn = ttk.Button(
            back_frame,
            text="＜戻る",
            command=self._on_back_btn_click,
            width=15
        )
        back_btn.pack(anchor='w')

    def _on_tag_toggle(self, tag: str):
        self.controller.toggle_tag(tag)

    def _on_category_toggle(self, category: str):
        self.controller.toggle_category(category)

    def _on_clear_all_click(self):
        self.controller.clear_all()

    def _on_select_all_tags_click(self):
        self.controller.select_all_tags()

    def _on_select_all_categories_click(self):
        self.controller.select_all_categories()

    def _on_state_changed(self, terms: list[str], summary_text: str, selected_tags: set[str], selected_categories: set[str]):
        """Controller から状態更新通知を受け取る"""
        # CheckBox の反映
        for tag, var in self.tag_vars.items():
            var.set(tag in selected_tags)
        for cat, var in self.category_vars.items():
            var.set(cat in selected_categories)
        # サマリー更新
        self.summary_label.config(text=summary_text)

    def _on_hide_words_click(self):
        """「単語を隠して出題」ボタンがクリックされた"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_hide_words()

    def _on_hide_explanations_click(self):
        """「説明を隠して出題」ボタンがクリックされた"""
        terms = self.controller.get_selected_terms()
        if not terms:
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_hide_explanations()

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

    