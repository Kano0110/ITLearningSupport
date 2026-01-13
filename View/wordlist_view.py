"""WordList画面のビュー層

用語一覧の表示、フィルタリングUI、検索バーなどのUI要素を管理します。
"""
import tkinter as tk
from tkinter import ttk, messagebox

# レイアウト定数
MAX_ROWS_PER_COLUMN = 20
NUM_COLUMNS = 3
SCROLL_UNITS = 3


class WordListView:
    """WordList画面のビュークラス
    
    用語一覧、フィルタ、検索機能のUIを提供します。
    コントローラとの連携により、データ取得と画面更新を行います。
    """
    
    def __init__(self, root: tk.Tk, controller):
        """WordListViewの初期化
        
        Args:
            root: Tkインスタンス
            controller: WordListControllerインスタンス
        """
        self.controller = controller
        self.root = root
        # コントローラ側でUIリセットに使う参照を持たせる
        self.controller.view = self
        # 画面全体をまとめるフレームを作る（表示/非表示はこの frame 単位で行う）
        self.frame = ttk.Frame(self.root, padding=0)
        # UI要素（frame 内に作る）
        self.search_var = None
        self.scrollable_frame = None
        self.canvas = None
        # build
        self._build_ui()
        # コントローラにコールバックを設定
        self.controller.set_view_update_callback(self.display_terms)

    # ==================== UI構築メソッド ====================
    
    def _build_ui(self):
        """UI全体を構築"""
        self._create_navigation_buttons()
        self._create_index_buttons()
        self._create_filter_selectors()
        self._create_search_bar()
        self._create_list_area()

    def _create_navigation_buttons(self):
        """ナビゲーションボタン（Home、WordEntry）を作成"""
        nav_frame = tk.Frame(self.frame, bg='#2C3E50')
        nav_frame.pack(fill='x', ipady=5, padx=40, pady=(20, 0))
        
        # タイトルラベル（中央配置）
        title_label = tk.Label(
            nav_frame,
            text="単語一覧",
            bg='#2C3E50',
            fg='white',
            font=('Arial', 18, 'bold')
        )
        title_label.pack(anchor='center', pady=(0, 0))
        
        # ナビゲーションボタン（色枠の外に配置）
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill='x', pady=20)
        
        # ボタンを中央に配置するためのサブフレーム
        center_buttons = ttk.Frame(button_frame)
        center_buttons.pack(expand=True)
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Home.TButton', foreground="#1523E6", font=('Arial', 11, 'bold'))
        style.configure('Quiz.TButton', foreground="#E67E22", font=('Arial', 11, 'bold'))
        style.configure('Entry.TButton', foreground="#099945", font=('Arial', 11, 'bold'))
        
        
        buttons = [
            ("Home", self.on_go_home_click, 'Home.TButton'),
            ("問題を解く", self.on_go_quiz_click, 'Quiz.TButton'),
            ("単語登録", self.on_go_wordentry_click, 'Entry.TButton')
        ]
        
        for text, command, style_name in buttons:
            btn = ttk.Button(center_buttons, text=text, command=command, style=style_name)
            btn.pack(side='left', padx=10, pady=5)

    def _create_index_buttons(self):
        """五十音インデックスボタンを作成"""
        index_frame = tk.Frame(self.frame, bg='#ECF0F1')
        index_frame.pack(fill='x', ipady=12)
        
        center_index = ttk.Frame(index_frame)
        center_index.pack(expand=True)
        
        # スタイル設定
        style = ttk.Style()
        style.configure('Yomi.TButton', foreground='#34495E', font=('Arial', 10))
        style.configure('AllYomi.TButton', foreground='#E74C3C', font=('Arial', 10, 'bold'))
        
        # 五十音インデックス取得
        yomi_keys = []
        try:
            yomi_keys = self.controller.get_yomi_index()
        except Exception:
            yomi_keys = self.controller.get_available_categories()
        
        # 五十音ボタン作成
        for key in yomi_keys:
            btn = ttk.Button(
                center_index, 
                text=key, 
                width=4, 
                command=lambda k=key: self.on_yomi_click(k),
                style='Yomi.TButton'
            )
            btn.pack(side='left', padx=3, pady=3)
        
        # その他ボタン
        other_btn = ttk.Button(
            center_index, 
            text="他", 
            width=5, 
            command=self.on_other_click,
            style='Yomi.TButton'
        )
        other_btn.pack(side='left', padx=3, pady=3)
        
        # 全て表示ボタン
        all_btn = ttk.Button(
            center_index, 
            text="全て", 
            width=5, 
            command=self.on_show_all_click,
            style='AllYomi.TButton'
        )
        all_btn.pack(side='left', padx=3, pady=3)

    def _create_filter_selectors(self):
        """タグとカテゴリのフィルタセレクタを作成"""
        filter_frame = ttk.Frame(self.frame, padding=(12, 8))
        filter_frame.pack(fill='x')
        
        center_filter = ttk.Frame(filter_frame)
        center_filter.pack(expand=True)
        
        # タグセレクタ
        self._create_single_filter(
            center_filter,
            "タグ:",
            self.controller.get_available_tags(),
            'tag_var',
            self.on_tag_selected,
            self.on_tag_clear_click,
            (0, 10)
        )
        
        # カテゴリセレクタ
        self._create_single_filter(
            center_filter,
            "カテゴリ:",
            self.controller.get_available_categories(),
            'category_var',
            self.on_category_selected,
            self.on_category_clear_click,
            (0, 10)
        )

        # フィルタ状態表示
        self._create_filter_status()
    
    def _create_single_filter(self, parent, label_text, items, var_name, on_select, on_clear, clear_padx):
        """単一のフィルタコンボボックスを作成
        
        Args:
            parent: 親ウィジェット
            label_text: ラベルテキスト
            items: コンボボックスの選択肢リスト
            var_name: StringVar属性名
            on_select: 選択時のコールバック
            on_clear: クリア時のコールバック
            clear_padx: クリアボタンのpadx設定
        """
        ttk.Label(parent, text=label_text).pack(side='left', padx=(5, 2))
        
        if items:
            var = tk.StringVar()
            setattr(self, var_name, var)
            combo = ttk.Combobox(
                parent, 
                textvariable=var, 
                values=items, 
                state='readonly', 
                width=12
            )
            combo.pack(side='left', padx=(0, 2))
            combo.bind('<<ComboboxSelected>>', on_select)
            
            clear_btn = ttk.Button(parent, text="×", width=3, command=on_clear)
            clear_btn.pack(side='left', padx=clear_padx)
        else:
            ttk.Label(parent, text="(なし)", foreground='gray').pack(
                side='left', 
                padx=clear_padx
            )
    
    def _create_filter_status(self):
        """フィルタ状態表示ラベルを作成"""
        status_frame = tk.Frame(self.frame, bg='#FFF3CD')
        status_frame.pack(fill='x', ipady=6, padx=8)
        
        tk.Label(
            status_frame, 
            text="絞り込み状況:", 
            bg='#FFF3CD',
            fg='#856404',
            font=('Arial', 11, 'bold')
        ).pack(side='left', padx=5)
        
        self.filter_status_label = tk.Label(
            status_frame, 
            text="", 
            fg='#0056B3', 
            bg='#FFF3CD',
            font=('Arial', 11, 'bold')
        )
        self.filter_status_label.pack(side='left', padx=5)

    def _create_search_bar(self):
        """検索バーと統計情報を作成"""
        search_frame = ttk.Frame(self.frame, padding=(10, 6))
        search_frame.pack(fill='x')
        center_search = ttk.Frame(search_frame)
        center_search.pack(expand=True)
        
        # 検索ラベル
        ttk.Label(center_search, text="絞り込み:").pack(side='left', padx=7)
        
        # 検索入力欄
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(center_search, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(6, 6))

        search_entry.bind('<KeyRelease>',  self.on_serach_change)
        self.after_id = None
        #self.search_var.trace_add('write', self.on_search_change)
        # Enterキーバインド
        #search_entry.bind('<Return>', self.on_search_enter)
        
        # クリアボタン
        clear_btn = ttk.Button(center_search, text="クリア", command=self.on_clear_search_click)
        clear_btn.pack(side='left', padx=8, pady=3)
        
        # 統計情報
        stats = self.controller.get_stats()
        total = stats.get('total', 0)
        stats_label = ttk.Label(
            center_search, 
            text=f"総用語数: {total}", 
            foreground='gray'
        )
        stats_label.pack(side='left', padx=10)

    def _create_list_area(self):
        """スクロール可能な用語リスト表示エリアを作成"""
        list_frame = ttk.Frame(self.frame, padding=(15, 5, 15, 8))
        list_frame.pack(expand=True, fill='both')

        # キャンバスとスクロールバー
        self.canvas = tk.Canvas(list_frame, background='white')
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        # スクロール可能な内部フレーム
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self._canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor='nw'
        )

        # スクロール領域の自動更新
        self.scrollable_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>", 
            lambda e: self.canvas.itemconfig(self._canvas_window, width=e.width)
        )

        # マウスホイールスクロールイベント
        self._bind_mousewheel_events(self.canvas)
    
    def _bind_mousewheel_events(self, widget):
        """マウスホイールイベントをウィジェットにバインド
        
        Args:
            widget: イベントをバインドするウィジェット
        """
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        widget.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down

    def _on_mousewheel(self, event):
        """マウスホイールスクロール処理
        
        内容がCanvas高さより小さい場合はスクロール操作を無視します。
        
        Args:
            event: マウスホイールイベント
        """
        canvas_height = self.canvas.winfo_height()
        content_height = self.scrollable_frame.winfo_reqheight()
        
        # 内容がCanvas以下の場合はスクロール不可
        if content_height <= canvas_height:
            return
        
        # スクロール方向の判定と実行
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(SCROLL_UNITS, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-SCROLL_UNITS, "units")
    
    # ==================== 用語表示メソッド ====================

    def display_terms(self, terms: list, message: str = None):
        """用語リストを表示
        
        Args:
            terms: 表示する用語名のリスト
            message: 用語がない場合に表示するメッセージ
        """
        # 既存のウィジェットをクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if terms:
            self._display_term_grid(terms)
        else:
            self._display_empty_message(message)

        # スクロール領域を更新
        self._update_scroll_region()
    
    def _display_term_grid(self, terms: list):
        """用語をグリッドレイアウトで表示
        
        Args:
            terms: 表示する用語名のリスト
        """
        for i, name in enumerate(terms):
            col_index = i % NUM_COLUMNS
            row_index = i // NUM_COLUMNS
            
            # 12文字以上の場合は省略表示
            display_text = name if len(name) < 12 else name[:11] + '…'
            
            lbl = ttk.Label(
                self.scrollable_frame,
                text=display_text,
                padding=(6, 8),
                cursor='hand2',
                anchor='center',
                justify='center',
                width=12,  # 固定幅を設定して均等に保つ
                font=('Arial', 10)
            )
            lbl.grid(row=row_index, column=col_index, sticky='ew', padx=1, pady=1)
            
            # イベントバインド
            lbl.bind('<Button-1>', lambda e, term=name: self.on_term_click(term))
            lbl.bind('<Enter>', lambda e, l=lbl: l.configure(foreground='#E67E22'))
            lbl.bind('<Leave>', lambda e, l=lbl: l.configure(foreground='black'))
            self._bind_mousewheel_events(lbl)

        # 各列を均等に広げる（同じ重みを設定）
        for col in range(NUM_COLUMNS):
            self.scrollable_frame.columnconfigure(col, weight=1, uniform='equal')
    
    def _display_empty_message(self, message: str = None):
        """用語がない場合のメッセージを表示
        
        Args:
            message: 表示するメッセージ（Noneの場合はデフォルトメッセージ）
        """
        if message is None:
            message = "用語が見つかりません"
        
        msg_label = ttk.Label(
            self.scrollable_frame, 
            text=message, 
            foreground='gray'
        )
        msg_label.grid(row=0, column=0, columnspan=NUM_COLUMNS, sticky='ew', padx=5, pady=20)
        
        # 各列を均等に広げる
        for col in range(NUM_COLUMNS):
            self.scrollable_frame.columnconfigure(col, weight=1)
    
    def _update_scroll_region(self):
        """スクロール領域を更新"""
        try:
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.frame.update()
        except Exception:
            pass
    
    # ==================== イベントハンドラ ====================

    def on_yomi_click(self, yomi_key: str):
        """五十音インデックスクリック時の処理
        
        Args:
            yomi_key: 五十音キー（"あ"、"か"など）
        """
        self.controller.select_yomi(yomi_key)

    def on_other_click(self):
        """その他ボタンクリック時の処理"""
        self.controller.select_other()

    def on_show_all_click(self):
        """全て表示ボタンクリック時の処理"""
        self.controller.reset_filters_to_all()
    def on_serach_change(self, *args):
        
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(300, self.apply_search)
    def apply_search(self):
        """検索テキスト変更時の処理
        
        Args:
            *args: trace_addからの引数（未使用）
        """
        query = self.search_var.get()
        self.controller.apply_search(query)

    def on_search_enter(self, event):
        """検索入力欄でEnterキー押下時の処理
        
        Args:
            event: Enterキーイベント
        """
        query = self.search_var.get()
        if query:
            self.controller.apply_search(query)

    def on_clear_search_click(self):
        """検索クリアボタンクリック時の処理"""
        self.search_var.set("")
        self.controller.clear_search()

    def on_tag_selected(self, event):
        """タグ選択時の処理
        
        Args:
            event: Comboboxイベント
        """
        tag = self.tag_var.get()
        if tag:
            self.controller.select_tag(tag)

    def on_tag_clear_click(self):
        """タグフィルタクリア時の処理"""
        self.tag_var.set("")
        self.controller.clear_tag()

    def on_category_selected(self, event):
        """カテゴリ選択時の処理
        
        Args:
            event: Comboboxイベント
        """
        category = self.category_var.get()
        if category:
            self.controller.select_category_db(category)
    
    def on_category_clear_click(self):
        """カテゴリフィルタクリア時の処理"""
        self.category_var.set("")
        self.controller.clear_category()

    def on_go_home_click(self):
        """Homeボタンクリック時の処理"""
        self.controller.go_to_home()

    def on_go_quiz_click(self):
        """問題を解くボタンクリック時の処理"""
        self.controller.go_to_quiz()

    def on_go_wordentry_click(self):
        """単語登録ボタンクリック時の処理"""
        self.controller.go_to_wordentry()

    def on_term_click(self, term: str):
        """用語クリック時の処理
        
        Args:
            term: クリックされた用語名
        """
        if hasattr(self.controller, "on_term_selected"):
            self.controller.on_term_selected(term)
        else:
            # フォールバック: 詳細情報をローカル表示
            detail = self.controller.get_term_detail(term)
            if detail:
                self._show_detail_window(detail)
            else:
                messagebox.showwarning("警告", f"'{term}'の詳細情報が見つかりません")

    def _show_detail_window(self, detail: dict):
        """詳細情報ウィンドウを表示
        
        Args:
            detail: 用語の詳細情報辞書
        """
        win = tk.Toplevel(self.root)
        win.title(detail.get("word_name", "詳細"))
        text = tk.Text(win, width=60, height=15)
        text.insert("1.0", str(detail))
        text.config(state='disabled')
        text.pack(fill='both', expand=True)
    
    # ==================== ライフサイクルメソッド ====================

    def show(self):
        """画面を表示"""
        self.frame.pack(expand=True, fill='both')
        try:
            self.root.update()
        except Exception:
            pass

    def hide(self):
        """画面を非表示"""
        # 検索の保留 after があればキャンセルして他画面への影響を防止
        try:
            if hasattr(self, 'after_id') and self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        except Exception:
            pass
        self.frame.pack_forget()