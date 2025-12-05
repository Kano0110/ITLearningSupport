# View/Q_SelectView.py
import tkinter as tk
from tkinter import ttk, messagebox

class Q_SelectView:
    """出題形式選択画面の View (タグ/カテゴリ マルチ選択対応)
    責務：UI 表示のみ。ビジネスロジックは一切含まない。
    """
    
    # 定数定義
    MAX_COLS_PER_ROW = 6
    TAG_CANVAS_HEIGHT = 50
    CATEGORY_CANVAS_HEIGHT = 45

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
        self.tags_canvas = None
        self.categories_canvas = None
        
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
        title_frame = tk.Frame(self.frame, bg='#4A90E2')
        title_frame.pack(fill='x', pady=20, padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="出題形式選択",
            font=('Arial', 18, 'bold'),
            bg='#4A90E2',
            fg='white'
        )
        title_label.pack(pady=5)

    def _create_multi_selectors(self):
        """タグ/カテゴリのチェックボックス群を作成（スクロール対応）"""
        outer = ttk.Frame(self.frame, padding=(20, 20, 20, 10))
        outer.pack(fill='both', expand=False)

        # タグ領域
        self.tags_canvas = self._create_scrollable_selector(
            outer, "タグ", self.TAG_CANVAS_HEIGHT
        )
        self.tags_container = self.tags_canvas.winfo_children()[0]
        self._build_tag_checkboxes()

        # カテゴリ領域
        self.categories_canvas = self._create_scrollable_selector(
            outer, "カテゴリ", self.CATEGORY_CANVAS_HEIGHT
        )
        self.categories_container = self.categories_canvas.winfo_children()[0]
        self._build_category_checkboxes()

        # 操作ボタン行
        self._create_operation_buttons(outer)

        # サマリー表示
        self._create_summary_label(outer)

    def _create_scrollable_selector(self, parent: ttk.Frame, label: str, height: int) -> tk.Canvas:
        """スクロール可能なセレクタ領域を作成
        
        Args:
            parent: 親フレーム
            label: ラベルテキスト
            height: キャンバスの高さ
            
        Returns:
            作成したキャンバス
        """
        frame = ttk.LabelFrame(parent, text=label, padding=10)
        frame.pack(fill='x', pady=(0, 10))
        
        canvas = tk.Canvas(frame, height=height)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=container, anchor='nw')
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # スクロール領域の自動更新
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        # マウスホイールスクロール
        self._bind_scroll_events(canvas, canvas)
        
        return canvas

    def _create_operation_buttons(self, parent: ttk.Frame):
        """操作ボタン（全解除/全選択）を作成"""
        ops_frame = ttk.Frame(parent)
        ops_frame.pack(fill='x', pady=(5, 5))
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Clear.TButton', foreground='#D9534F')
        style.configure('SelectTag.TButton', foreground='#5CB85C')
        style.configure('SelectCat.TButton', foreground='#5BC0DE')
        
        buttons = [
            ("全て解除", self._on_clear_all_click, 12, 'Clear.TButton'),
            ("タグ全選択", self._on_select_all_tags_click, 12, 'SelectTag.TButton'),
            ("カテゴリ全選択", self._on_select_all_categories_click, 12, 'SelectCat.TButton')
        ]
        
        for text, command, width, style_name in buttons:
            btn = ttk.Button(ops_frame, text=text, command=command, width=width, style=style_name)
            btn.pack(side='left', padx=(0, 10))

    def _create_summary_label(self, parent: ttk.Frame):
        """サマリー表示ラベルを作成"""
        summary_frame = tk.Frame(parent, bg='#F0F0F0')
        summary_frame.pack(fill='x', pady=(10, 0), padx=10, ipady=8)
        self.summary_label = tk.Label(
            summary_frame, 
            text="全て (0個)", 
            font=('Arial', 10, 'bold'), 
            fg='#333333',
            bg='#F0F0F0'
        )
        self.summary_label.pack(side='left', padx=5)

    def _build_tag_checkboxes(self):
        """タグチェックボックスを構築"""
        self._build_checkboxes(
            container=self.tags_container,
            items=self.controller.get_available_tags(),
            vars_dict=self.tag_vars,
            toggle_callback=self._on_tag_toggle,
            canvas=self.tags_canvas,
            empty_message="タグなし"
        )

    def _build_category_checkboxes(self):
        """カテゴリチェックボックスを構築"""
        self._build_checkboxes(
            container=self.categories_container,
            items=self.controller.get_available_categories(),
            vars_dict=self.category_vars,
            toggle_callback=self._on_category_toggle,
            canvas=self.categories_canvas,
            empty_message="カテゴリなし"
        )

    def _build_checkboxes(self, container: ttk.Frame, items: list, vars_dict: dict, 
                         toggle_callback: callable, canvas: tk.Canvas, empty_message: str):
        """汎用チェックボックス構築メソッド
        
        Args:
            container: チェックボックスを配置するコンテナ
            items: チェックボックスに表示するアイテムリスト
            vars_dict: BooleanVar を格納する辞書
            toggle_callback: チェックボックストグル時のコールバック
            canvas: スクロール用キャンバス
            empty_message: アイテムがない場合のメッセージ
        """
        # 既存のウィジェットをクリア
        for widget in container.winfo_children():
            widget.destroy()
        
        if not items:
            ttk.Label(container, text=empty_message, foreground='gray').pack(anchor='w')
            return
        
        # コンテナにスクロールイベントをバインド
        self._bind_scroll_events(container, canvas)
        
        # チェックボックスを横並びで配置（1行6個まで）
        row_frame = self._create_checkbox_row(container, canvas)
        col_count = 0
        max_cols_per_row = 6
        
        for item in items:
            var = vars_dict.get(item) or tk.BooleanVar(value=False)
            vars_dict[item] = var
            
            # 10文字以上の場合は省略表示
            display_text = item if len(item) < 10 else item[:9] + '…'
            
            cb = ttk.Checkbutton(
                row_frame, 
                text=display_text, 
                variable=var, 
                command=lambda i=item: toggle_callback(i)
            )
            cb.pack(side='left', padx=4, pady=2)
            self._bind_scroll_events(cb, canvas)
            
            col_count += 1
            if col_count >= max_cols_per_row:
                row_frame = self._create_checkbox_row(container, canvas)
                col_count = 0

    def _create_checkbox_row(self, parent: ttk.Frame, canvas: tk.Canvas) -> ttk.Frame:
        """チェックボックス配置用の行フレームを作成
        
        Args:
            parent: 親フレーム
            canvas: スクロール用キャンバス
            
        Returns:
            作成した行フレーム
        """
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill='x', anchor='w')
        self._bind_scroll_events(row_frame, canvas)
        return row_frame

    def _bind_scroll_events(self, widget: tk.Widget, canvas: tk.Canvas):
        """ウィジェットにスクロールイベントをバインド
        
        Args:
            widget: イベントをバインドするウィジェット
            canvas: スクロール対象のキャンバス
        """
        widget.bind("<MouseWheel>", lambda e: self._on_canvas_scroll(e, canvas))
        widget.bind("<Button-4>", lambda e: self._on_canvas_scroll(e, canvas))
        widget.bind("<Button-5>", lambda e: self._on_canvas_scroll(e, canvas))

    def _create_quiz_buttons(self):
        """出題ボタンを作成"""
        buttons_frame = ttk.Frame(self.frame, padding=(20, 0, 20, 10))
        buttons_frame.pack(fill='both', expand=True)

        inner_buttons_frame = ttk.Frame(buttons_frame)
        inner_buttons_frame.pack(expand=True)

        quiz_buttons = [
            ("単語を隠して出題", self._on_hide_words_click, 'Quiz1.TButton'),
            ("説明を隠して出題", self._on_hide_explanations_click, 'Quiz2.TButton')
        ]
        
        for text, command, style_name in quiz_buttons:
            btn = ttk.Button(inner_buttons_frame, text=text, command=command, width=20, style=style_name)
            btn.pack(side='left', padx=20, pady=20)

    def _create_back_button(self):
        """戻るボタンを作成"""
        back_frame = ttk.Frame(self.frame, padding=(20, 0, 20, 10))
        back_frame.pack(fill='x')
        
        back_btn = ttk.Button(back_frame, text="＜戻る", command=self._on_back_btn_click, width=15)
        back_btn.pack(anchor='w')

    def _on_canvas_scroll(self, event, canvas: tk.Canvas):
        """キャンバスのマウスホイールスクロール処理
        
        Args:
            event: スクロールイベント
            canvas: スクロール対象のキャンバス
        """
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")

    # --- イベントハンドラ ---
    def _on_tag_toggle(self, tag: str):
        """タグチェックボックストグル時の処理"""
        self.controller.toggle_tag(tag)

    def _on_category_toggle(self, category: str):
        """カテゴリチェックボックストグル時の処理"""
        self.controller.toggle_category(category)

    def _on_clear_all_click(self):
        """全て解除ボタンクリック時の処理"""
        self.controller.clear_all()

    def _on_select_all_tags_click(self):
        """タグ全選択ボタンクリック時の処理"""
        self.controller.select_all_tags()

    def _on_select_all_categories_click(self):
        """カテゴリ全選択ボタンクリック時の処理"""
        self.controller.select_all_categories()

    def _on_state_changed(self, terms: list[str], summary_text: str, 
                         selected_tags: set[str], selected_categories: set[str]):
        """Controllerから状態更新通知を受け取る
        
        Args:
            terms: フィルタリングされた用語リスト
            summary_text: サマリーテキスト
            selected_tags: 選択中のタグセット
            selected_categories: 選択中のカテゴリセット
        """
        for tag, var in self.tag_vars.items():
            var.set(tag in selected_tags)
        for cat, var in self.category_vars.items():
            var.set(cat in selected_categories)
        self.summary_label.config(text=summary_text)

    def _on_hide_words_click(self):
        """単語を隠して出題ボタンクリック時の処理"""
        if not self.controller.get_selected_terms():
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_hide_words()

    def _on_hide_explanations_click(self):
        """説明を隠して出題ボタンクリック時の処理"""
        if not self.controller.get_selected_terms():
            messagebox.showwarning("警告", "用語が選択されていません")
            return
        self.controller.start_quiz_hide_explanations()

    def _on_back_btn_click(self):
        """戻るボタンクリック時の処理"""
        self.controller.go_to_home()

    # --- 公開メソッド ---
    def show(self):
        """Viewを表示（AppControllerから呼ばれる）"""
        self.frame.pack(expand=True, fill='both')
        try:
            self.root.update()
        except Exception:
            pass

    def hide(self):
        """Viewを非表示（AppControllerから呼ばれる）"""
        self.frame.pack_forget()

    