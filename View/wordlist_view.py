import tkinter as tk
from tkinter import ttk, messagebox

MAX_ROWS_PER_COLUMN = 20

class WordListView:
    def __init__(self, root: tk.Tk, controller):
        self.controller = controller
        self.root = root
        # 画面全体をまとめるフレームを作る（表示/非表示はこの frame 単位で行う）
        self.frame = ttk.Frame(self.root, padding=0)
        # UI要素（frame 内に作る）
        self.search_var = None
        self.scrollable_frame = None
        self.canvas = None
        # build
        self._build_ui()
        # コントローラにコールバックを設定
        # controller は set_view_update_callback で display_terms を登録する想定
        self.controller.set_view_update_callback(self.display_terms)

    def _build_ui(self):
        self._create_navigation_buttons()
        self._create_index_buttons()
        self._create_tag_selector()
        self._create_search_bar()
        self._create_list_area()

    def _create_navigation_buttons(self):
        """ナビゲーションボタン（Home、WordEntry）を作成"""
        nav_frame = ttk.Frame(self.frame, padding=8)
        nav_frame.pack(fill='x')
        
        # 中央に配置するための内側フレーム
        center_nav = ttk.Frame(nav_frame)
        center_nav.pack(expand=True)
        
        home_btn = ttk.Button(center_nav, text="← Home", command=self.on_go_home_click)
        home_btn.pack(side='left', padx=5)
        
        entry_btn = ttk.Button(center_nav, text="単語登録 →", command=self.on_go_wordentry_click)
        entry_btn.pack(side='left', padx=5)

    def _create_index_buttons(self):
        """カテゴリボタン（五十音図）を作成"""
        index_frame = ttk.Frame(self.frame, padding=8)
        index_frame.pack(fill='x')
        
        # 中央に配置するための内側フレーム
        center_index = ttk.Frame(index_frame)
        center_index.pack(expand=True)
        
        categories = self.controller.get_available_categories()
        for category in categories:
            btn = ttk.Button(center_index, text=category, width=3, command=lambda c=category: self.on_category_click(c))
            btn.pack(side='left', padx=2)
        all_btn = ttk.Button(center_index, text="全て", width=4, command=self.on_show_all_click)
        all_btn.pack(side='left', padx=2)

    def _create_tag_selector(self):
        """タグで絞り込むUIを作成"""
        tag_frame = ttk.Frame(self.frame, padding=(8, 4))
        tag_frame.pack(fill='x')
        
        # 中央に配置するための内側フレーム
        center_tag = ttk.Frame(tag_frame)
        center_tag.pack(expand=True)
        
        ttk.Label(center_tag, text="タグ:").pack(side='left', padx=5)
        
        tags = self.controller.get_available_tags()
        if tags:
            self.tag_var = tk.StringVar()
            tag_combo = ttk.Combobox(center_tag, textvariable=self.tag_var, values=tags, state='readonly', width=20)
            tag_combo.pack(side='left', padx=(4, 4))
            tag_combo.bind('<<ComboboxSelected>>', self.on_tag_selected)
            
            tag_clear_btn = ttk.Button(center_tag, text="タグクリア", command=self.on_tag_clear_click)
            tag_clear_btn.pack(side='left', padx=5)
        else:
            ttk.Label(center_tag, text="利用可能なタグはありません", foreground='gray').pack(side='left')

    def _create_search_bar(self):
        search_frame = ttk.Frame(self.frame, padding=(8, 4))
        search_frame.pack(fill='x')
        
        # 中央に配置するための内側フレーム
        center_search = ttk.Frame(search_frame)
        center_search.pack(expand=True)
        
        ttk.Label(center_search, text="絞り込み:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(center_search, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(4, 4))
        self.search_var.trace_add('write', self.on_search_change)
        clear_btn = ttk.Button(center_search, text="クリア", command=self.on_clear_search_click)
        clear_btn.pack(side='left', padx=5)
        
        stats = self.controller.get_stats()
        total = stats.get('total', 0)
        stats_label = ttk.Label(center_search, text=f"総用語数: {total}", foreground='gray')
        stats_label.pack(side='left', padx=10)

    def _create_list_area(self):
        list_frame = ttk.Frame(self.frame, padding=8)
        list_frame.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(list_frame, background='white')
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        # 内部フレームは白背景の tk.Frame にして、白い領域に単語を描画する
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self._canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        # 中身のサイズ変化に合わせて scrollregion を更新する
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Canvas の幅が変わったら内部ウィンドウの幅を合わせる（ラベルを横幅いっぱいにするため）
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._canvas_window, width=e.width))

        # マウスホイールスクロール機能を追加
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down

    def _on_mousewheel(self, event):
        """マウスホイールスクロール処理
        
        内容がCanvas高さより小さい場合はスクロール操作を無視します。
        """
        # Windows: event.delta > 0 で上方向、< 0 で下方向
        # Linux: Button-4 で上方向、Button-5 で下方向
        
        # Canvas と内容フレームの高さを取得
        canvas_height = self.canvas.winfo_height()
        content_height = self.scrollable_frame.winfo_reqheight()
        
        # 内容がCanvas以下の場合はスクロール不可
        if content_height <= canvas_height:
            return
        
        if event.num == 5 or event.delta < 0:
            # 下方向スクロール
            self.canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:
            # 上方向スクロール
            self.canvas.yview_scroll(-3, "units")

    def display_terms(self, terms: list, message: str = None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if terms:
            # 左から順に埋める 3 列レイアウト（行優先）
            NUM_COLUMNS = 3
            for i, name in enumerate(terms):
                col_index = i % NUM_COLUMNS
                row_index = i // NUM_COLUMNS
                lbl = ttk.Label(
                    self.scrollable_frame,
                    text=name,
                    padding=(6, 5),
                    cursor='hand2',
                    anchor='center',
                    justify='center'
                )
                lbl.grid(row=row_index, column=col_index, sticky='ew', padx=5, pady=2)
                lbl.bind('<Button-1>', lambda e, term=name: self.on_term_click(term))
                lbl.bind('<Enter>', lambda e, l=lbl: l.configure(foreground='blue'))
                lbl.bind('<Leave>', lambda e, l=lbl: l.configure(foreground='black'))
                # マウスホイールイベントも受け取らせる
                lbl.bind('<MouseWheel>', self._on_mousewheel)
                lbl.bind('<Button-4>', self._on_mousewheel)
                lbl.bind('<Button-5>', self._on_mousewheel)

            # 各列を均等に広げる
            for col in range(NUM_COLUMNS):
                self.scrollable_frame.columnconfigure(col, weight=1)
        else:
            if message is None:
                message = "用語が見つかりません"
            ttk.Label(self.scrollable_frame, text=message, foreground='gray').grid(row=0, column=0, sticky='w')

        try:
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.frame.update()
        except Exception:
            pass

    def on_category_click(self, category: str):
        self.controller.select_category(category)

    def on_show_all_click(self):
        self.controller.clear_category()

    def on_search_change(self, *args):
        query = self.search_var.get()
        self.controller.apply_search(query)

    def on_clear_search_click(self):  # 検索窓のリセット
        self.search_var.set("")
        self.controller.clear_search()

    def on_tag_selected(self, event):
        """タグが選択された時の処理"""
        tag = self.tag_var.get()
        if tag:
            self.controller.select_tag(tag)

    def on_tag_clear_click(self):
        """タグフィルタをクリア"""
        self.tag_var.set("")
        self.controller.clear_tag()

    def on_go_home_click(self):
        """Home画面への遷移"""
        self.controller.go_to_home()

    def on_go_wordentry_click(self):
        """WordEntry画面への遷移"""
        self.controller.go_to_wordentry()

    def on_term_click(self, term: str):
        """用語がクリックされた時の処理。Controller に通知して遷移させる。"""
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
        win = tk.Toplevel(self.root)
        win.title(detail.get("word_name", "詳細"))
        text = tk.Text(win, width=60, height=15)
        text.insert("1.0", str(detail))
        text.config(state='disabled')
        text.pack(fill='both', expand=True)

    def show(self):
        """AppController から呼ばれる表示メソッド"""
        #print("WordListView.show called")
        self.frame.pack(expand=True, fill='both')
        try:
            self.root.update()
        except Exception:
            pass

    def hide(self):
        """AppController から呼ばれる非表示メソッド"""
        self.frame.pack_forget()