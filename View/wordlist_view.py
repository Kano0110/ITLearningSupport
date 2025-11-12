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
        self._create_index_buttons()
        self._create_search_bar()
        self._create_list_area()

    def _create_index_buttons(self):
        index_frame = ttk.Frame(self.frame, padding=8)
        index_frame.pack(fill='x')
        categories = self.controller.get_available_categories()
        for category in categories:
            btn = ttk.Button(index_frame, text=category, width=3, command=lambda c=category: self.on_category_click(c))
            btn.pack(side='left', padx=2)
        all_btn = ttk.Button(index_frame, text="全て", width=4, command=self.on_show_all_click)
        all_btn.pack(side='left', padx=2)

    def _create_search_bar(self):
        search_frame = ttk.Frame(self.frame, padding=(8, 4))
        search_frame.pack(fill='x')
        ttk.Label(search_frame, text="絞り込み:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(6, 4))
        self.search_var.trace_add('write', self.on_search_change)
        clear_btn = ttk.Button(search_frame, text="クリア", command=self.on_clear_search_click)
        clear_btn.pack(side='left')
        stats = self.controller.get_stats()
        total = stats.get('total', 0)
        stats_label = ttk.Label(search_frame, text=f"総用語数: {total}", foreground='gray')
        stats_label.pack(side='right', padx=10)

    def _create_list_area(self):
        list_frame = ttk.Frame(self.frame, padding=8)
        list_frame.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(list_frame, background='white')
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        # 中身のサイズ変化に合わせて scrollregion を更新する
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def display_terms(self, terms: list, message: str = None):
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if terms:
            for i, name in enumerate(terms):
                row_index = i % MAX_ROWS_PER_COLUMN
                col_index = i // MAX_ROWS_PER_COLUMN
                lbl = ttk.Label(self.scrollable_frame, text=name, padding=(4, 2), cursor='hand2')
                lbl.grid(row=row_index, column=col_index, sticky='w')
                lbl.bind('<Button-1>', lambda e, term=name: self.on_term_click(term))
                lbl.bind('<Enter>', lambda e, l=lbl: l.configure(foreground='blue'))
                lbl.bind('<Leave>', lambda e, l=lbl: l.configure(foreground='black'))
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