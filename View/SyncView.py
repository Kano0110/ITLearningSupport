import tkinter as tk
from tkinter import ttk, messagebox
import math

class LoginDialog(tk.Toplevel):
    """サーバー接続情報入力用ダイアログ"""
    def __init__(self, parent, on_confirm):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.title("サーバー接続")
        self.geometry("320x220")
        self.resizable(False, False)
        self.configure(bg="#F5F5F7")
        self.transient(parent)
        self.grab_set()
        
        # 画面中央配置
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (160)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (110)
        self.geometry(f"+{x}+{y}")
        
        self._create_ui()

    def _create_ui(self):
        frame = tk.Frame(self, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="ユーザー名", bg="#FFFFFF", fg="#666").pack(anchor="w")
        self.entry_user = ttk.Entry(frame, width=30)
        self.entry_user.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="パスワード", bg="#FFFFFF", fg="#666").pack(anchor="w")
        self.entry_pass = ttk.Entry(frame, show="●", width=30)
        self.entry_pass.pack(fill="x", pady=(0, 15))

        btn_frame = tk.Frame(frame, bg="#FFFFFF")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        tk.Button(btn_frame, text="キャンセル", command=self.destroy, bg="#E5E5EA", relief="flat", padx=10).pack(side="left")
        tk.Button(btn_frame, text="接続", command=self._on_connect, bg="#007AFF", fg="white", relief="flat", padx=15).pack(side="right")

    def _on_connect(self):
        self.on_confirm(self.entry_user.get(), self.entry_pass.get())
        self.destroy()

class FilterDialog(tk.Toplevel):
    """
    「条件で選択」ボタンを押したときのモーダルウィンドウ
    画像右側のデザインを再現
    """
    def __init__(self, parent, categories, tags, on_apply):
        super().__init__(parent)
        self.on_apply = on_apply
        self.title("条件で選択")
        self.geometry("450x400")
        self.configure(bg="#FFFFFF")
        self.transient(parent)
        self.grab_set()
        
        # 変数
        self.search_var = tk.StringVar()
        self.tag_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.categories = categories
        self.tags = tags
        
        # 画面中央配置
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (225)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (200)
        self.geometry(f"+{x}+{y}")

        self._create_ui()

    def _create_ui(self):
        pad_opts = {'padx': 15, 'pady': 10}
        
        # --- 絞り込み（検索） ---
        row1 = tk.Frame(self, bg="#FFFFFF")
        row1.pack(fill='x', **pad_opts)
        tk.Label(row1, text="絞り込み：", bg="#FFFFFF").pack(side='left')
        ttk.Entry(row1, textvariable=self.search_var).pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(row1, text="クリア", bg="#FFFFFF", relief="solid", bd=1, command=lambda: self.search_var.set("")).pack(side='left')

        # --- タグ ---
        row2 = tk.Frame(self, bg="#FFFFFF")
        row2.pack(fill='x', **pad_opts)
        tk.Label(row2, text="タグ：　　", bg="#FFFFFF").pack(side='left')
        cb_tag = ttk.Combobox(row2, textvariable=self.tag_var, values=self.tags, state="readonly")
        cb_tag.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(row2, text="×", bg="#FFFFFF", relief="solid", bd=1, width=2, command=lambda: self.tag_var.set("")).pack(side='left')

        # --- カテゴリ ---
        row3 = tk.Frame(self, bg="#FFFFFF")
        row3.pack(fill='x', **pad_opts)
        tk.Label(row3, text="カテゴリ：", bg="#FFFFFF").pack(side='left')
        cb_cat = ttk.Combobox(row3, textvariable=self.category_var, values=self.categories, state="readonly")
        cb_cat.pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(row3, text="×", bg="#FFFFFF", relief="solid", bd=1, width=2, command=lambda: self.category_var.set("")).pack(side='left')

        # --- 五十音 ---
        frame_kana = tk.Frame(self, bg="#FFFFFF")
        frame_kana.pack(fill='x', padx=15, pady=20)
        
        kanas = [
            ['あ', 'か', 'さ', 'た', 'な'],
            ['は', 'ま', 'や', 'ら', 'わ']
        ]
        
        for r_idx, row in enumerate(kanas):
            row_f = tk.Frame(frame_kana, bg="#FFFFFF")
            row_f.pack(anchor='w', pady=2)
            for char in row:
                tk.Button(row_f, text=char, width=4, bg="#FFFFFF", relief="solid", bd=1,
                          command=lambda c=char: self._apply_kana(c)).pack(side='left', padx=2)
        
        # 「他」ボタン
        tk.Button(frame_kana, text="他", width=4, bg="#FFFFFF", relief="solid", bd=1,
                  command=lambda: self._apply_kana("other")).place(x=250, y=30) # 簡易配置

        # --- 決定ボタン ---
        tk.Button(self, text="この条件で絞り込む", bg="#007AFF", fg="white", font=("Arial", 10, "bold"),
                  relief="flat", pady=8, command=self._on_apply).pack(fill='x', padx=20, pady=20, side='bottom')

    def _apply_kana(self, char):
        # 簡易的に検索ボックスに文字を入れて適用扱いに
        self.on_apply({"search": "", "tag": "", "category": "", "kana": char})
        self.destroy()

    def _on_apply(self):
        filters = {
            "search": self.search_var.get(),
            "tag": self.tag_var.get(),
            "category": self.category_var.get(),
            "kana": None
        }
        self.on_apply(filters)
        self.destroy()

class SyncView(tk.Frame):
    """
    Apple風デザインのアップロード/ダウンロード画面
    画像のようなタブ切り替えとリスト表示を実装
    """
    COLOR_BG = "#F5F5F7"       # 背景グレー
    COLOR_CARD = "#FFFFFF"     # カード白
    COLOR_PRIMARY = "#007AFF"  # 青
    COLOR_TEXT = "#333333"
    COLOR_TAB_ACTIVE = "#A0A0A0" # タブのアクティブ色（画像ではグレー）
    COLOR_TAB_INACTIVE = "#FFFFFF"

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(bg=self.COLOR_BG)
        
        # 状態管理
        self.mode = "upload" # upload or download
        self.is_connected = False
        self.term_vars = {} # {uuid: BooleanVar}
        self.all_terms = [] # 全データキャッシュ
        
        self._build_ui()

    def _build_ui(self):
        # メインコンテナ
        container = tk.Frame(self, bg=self.COLOR_BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # === 1. タブエリア ===
        self.tabs_frame = tk.Frame(container, bg=self.COLOR_BG)
        self.tabs_frame.pack(fill="x", anchor="w")

        # タブの見た目はLabelで作成し、クリックイベントで切り替える
        self.tab_upload = tk.Label(self.tabs_frame, text="アップロード画面", font=("Yu Gothic UI", 12),
                                   width=18, pady=8, cursor="hand2", relief="solid", bd=1)
        self.tab_upload.pack(side="left")
        self.tab_upload.bind("<Button-1>", lambda e: self.switch_mode("upload"))

        self.tab_download = tk.Label(self.tabs_frame, text="ダウンロード画面", font=("Yu Gothic UI", 12),
                                     width=18, pady=8, cursor="hand2", relief="solid", bd=1)
        self.tab_download.pack(side="left")
        self.tab_download.bind("<Button-1>", lambda e: self.switch_mode("download"))

        # === 2. メインカードエリア ===
        self.card = tk.Frame(container, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground="#CCC")
        self.card.pack(fill="both", expand=True)

        # --- アクションボタンエリア ---
        action_frame = tk.Frame(self.card, bg=self.COLOR_CARD, pady=15, padx=20)
        action_frame.pack(fill="x")

        self.btn_action = tk.Button(action_frame, text="↑ 単語をアップロード", 
                                    bg=self.COLOR_PRIMARY, fg="white", font=("Yu Gothic UI", 12, "bold"),
                                    relief="flat", padx=20, pady=8, cursor="hand2",
                                    command=self._on_action_click)
        self.btn_action.pack(anchor="w")

        # --- ツールバーエリア (全選択 | 条件で選択 | 並び替え) ---
        toolbar = tk.Frame(self.card, bg=self.COLOR_CARD, padx=20, pady=5)
        toolbar.pack(fill="x")

        self.var_select_all = tk.BooleanVar()
        self.chk_all = tk.Checkbutton(toolbar, text="すべて選択", variable=self.var_select_all, 
                                      bg=self.COLOR_CARD, activebackground=self.COLOR_CARD,
                                      command=self._toggle_select_all)
        self.chk_all.pack(side="left")

        tk.Frame(toolbar, width=1, height=20, bg="#EEE").pack(side="left", padx=10) # 仕切り線

        self.btn_filter = tk.Button(toolbar, text="条件で選択 (ボタン)", relief="flat", bg=self.COLOR_CARD, 
                                    cursor="hand2", command=self._show_filter_dialog)
        self.btn_filter.pack(side="left")

        self.lbl_sort = tk.Label(toolbar, text="並び替え ▽", bg=self.COLOR_CARD, fg="#666", cursor="hand2")
        self.lbl_sort.pack(side="left", padx=20)

        # --- リスト表示エリア (スクロール付き) ---
        list_container = tk.Frame(self.card, bg=self.COLOR_CARD)
        list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(list_container, bg=self.COLOR_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLOR_CARD)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=600) # widthは仮
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # リサイズ対応
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # --- フッター (ステータス & ホーム戻る) ---
        footer_frame = tk.Frame(self.card, bg=self.COLOR_CARD, pady=15)
        footer_frame.pack(fill="x", side="bottom")

        # ステータス
        self.status_icon = tk.Label(footer_frame, text="●", fg="#CCC", bg=self.COLOR_CARD)
        self.status_icon.pack(side="top")
        self.status_text = tk.Label(footer_frame, text="未接続 - ボタンを押すとログイン画面が開きます", 
                                    fg="#CCC", bg=self.COLOR_CARD, font=("Yu Gothic UI", 9))
        self.status_text.pack(side="top", pady=(0, 10))

        # ホームへ戻る
        btn_home = tk.Button(footer_frame, text="🏠 ホームへ戻る", command=self.controller.go_to_home,
                             bg="#F0F0F0", relief="flat", padx=15, pady=5)
        btn_home.pack(side="top")


    def _on_canvas_configure(self, event):
        """キャンバスのリサイズに合わせて内部フレームの幅を調整"""
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def switch_mode(self, mode):
        """アップロード/ダウンロード画面の切り替え"""
        self.mode = mode
        
        # タブの色切り替え (画像参照: アクティブがグレー、非アクティブが白)
        active_bg = "#A0A0A0" # 濃いグレー
        active_fg = "white"
        inactive_bg = "#FFFFFF"
        inactive_fg = "#333"

        if mode == "upload":
            self.tab_upload.config(bg=active_bg, fg=active_fg)
            self.tab_download.config(bg=inactive_bg, fg=inactive_fg)
            self.btn_action.config(text="↑ 単語をアップロード", bg=self.COLOR_PRIMARY)
            # コントローラー経由でローカルデータを取得して表示
            self.controller.load_local_data()
            
        else:
            self.tab_download.config(bg=active_bg, fg=active_fg)
            self.tab_upload.config(bg=inactive_bg, fg=inactive_fg)
            self.btn_action.config(text="↓ 単語をダウンロード", bg="#34C759") # 緑系
            # コントローラー経由でサーバーデータを取得（未接続なら空など）
            self.controller.load_server_data()

    def update_term_list(self, terms):
        """
        リストを更新する
        terms: list of dict {'uuid':..., 'word_name':..., 'explain':...}
        """
        self.all_terms = terms
        self.term_vars = {}
        
        # 既存アイテム削除
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not terms:
            tk.Label(self.scrollable_frame, text="データがありません", bg=self.COLOR_CARD, fg="#999").pack(pady=20)
            return

        # アイテム生成 (画像のようなカードスタイル)
        for term in terms:
            var = tk.BooleanVar(value=False)
            self.term_vars[term['uuid']] = var
            
            item_frame = tk.Frame(self.scrollable_frame, bg=self.COLOR_CARD, bd=1, relief="solid")
            # 枠線の色を薄くしたいがtk.Frameでは限界があるため、簡易的にsolid
            # 実際にはCanvasで描画するか、Frameの中にFrameを入れると綺麗になる
            
            # アイテム行
            row = tk.Frame(self.scrollable_frame, bg="#FFFFFF", highlightbackground="#E5E5E5", highlightthickness=1, padx=10, pady=10)
            row.pack(fill="x", pady=2, padx=5)
            
            chk = tk.Checkbutton(row, variable=var, bg="#FFFFFF", activebackground="#FFFFFF")
            chk.pack(side="left")
            
            # テキスト部分
            text_frame = tk.Frame(row, bg="#FFFFFF")
            text_frame.pack(side="left", fill="x", expand=True, padx=10)
            
            tk.Label(text_frame, text=term.get('word_name', 'No Name'), font=("Yu Gothic UI", 11, "bold"), bg="#FFFFFF").pack(anchor="w")
            
            desc = term.get('explain', '')
            if len(desc) > 30: desc = desc[:30] + "..."
            tk.Label(text_frame, text=desc, font=("Yu Gothic UI", 9), fg="#666", bg="#FFFFFF").pack(anchor="w")

    def _toggle_select_all(self):
        """すべて選択/解除"""
        state = self.var_select_all.get()
        for var in self.term_vars.values():
            var.set(state)

    def _show_filter_dialog(self):
        """条件選択モーダルを表示"""
        # コントローラーからタグ・カテゴリ一覧を取得する想定
        cats = self.controller.get_categories()
        tags = self.controller.get_tags()
        FilterDialog(self, cats, tags, self._apply_filter)

    def _apply_filter(self, filters):
        """フィルタ適用"""
        print(f"Applying filters: {filters}")
        # 簡易実装: 文字列検索のみ反映（本格的にはControllerで絞り込むべき）
        filtered = []
        search_key = filters.get("search", "")
        
        for term in self.all_terms:
            if search_key in term.get('word_name', '') or search_key in term.get('explain', ''):
                filtered.append(term)
        
        # リスト再描画
        # 注: ここではUI上の再描画だけ行う。本来はControllerに依頼してデータを絞り込むのが綺麗。
        self.update_term_list(filtered)

    def _on_action_click(self):
        """アップロード/ダウンロードボタン押下"""
        selected_uuids = [uuid for uuid, var in self.term_vars.items() if var.get()]
        
        if not selected_uuids:
            messagebox.showwarning("警告", "単語が選択されていません")
            return

        if self.mode == "upload":
            self.controller.handle_upload_request(selected_uuids)
        else:
            self.controller.handle_download_request(selected_uuids)

    # --- Controllerから呼ばれるメソッド ---
    def show_login_dialog(self, callback):
        LoginDialog(self, callback)

    def update_status(self, is_connected, message):
        self.is_connected = is_connected
        if is_connected:
            self.status_icon.config(fg="#34C759") # 緑
            self.status_text.config(text=message, fg="#333")
        else:
            self.status_icon.config(fg="#CCC")
            self.status_text.config(text=message, fg="#CCC")

    def show_message(self, title, msg, is_error=False):
        if is_error:
            messagebox.showerror(title, msg, parent=self)
        else:
            messagebox.showinfo(title, msg, parent=self)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()