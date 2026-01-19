import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox  # messageboxを追加

class AuthView(tk.Frame):
    """
    画像のデザインを再現した認証画面 View
    （日本語入力制限機能 + エラーポップアップ付き）
    """
    
    # カラーパレット
    COLOR_PRIMARY = "#2C8CBE"   # 濃い青
    COLOR_BG = "#F5F5F5"        # 全体背景の薄いグレー
    COLOR_WHITE = "#FFFFFF"
    COLOR_TEXT = "#333333"
    
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(bg=self.COLOR_BG)
        
        # 状態管理 (True: ログインモード, False: 新規登録モード)
        self.is_login_mode = True
        
        # 入力値
        self.login_id_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # フォント設定
        self.font_header = tkfont.Font(family="Yu Gothic UI", size=20, weight="bold")
        self.font_label = tkfont.Font(family="Yu Gothic UI", size=11, weight="bold")
        self.font_tab = tkfont.Font(family="Yu Gothic UI", size=12, weight="bold")
        
        self._create_ui()

    def _validate_ascii(self, P):
        """
        入力バリデーション: ASCII文字（半角英数字・記号）のみ許可
        ASCII以外が含まれていた場合、ポップアップを出して入力を拒否する
        """
        if P == "":
            return True
            
        if not P.isascii():
            # ▼ ここでポップアップを表示
            # parent=self を指定して、この画面の手前に表示させる
            messagebox.showwarning("入力エラー", "半角英数字のみ入力可能です。", parent=self)
            return False
            
        return True

    def _create_ui(self):
        # 全体の中央配置用コンテナ
        center_frame = tk.Frame(self, bg=self.COLOR_BG)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # バリデーションコマンドの登録
        vcmd = (self.register(self._validate_ascii), '%P')

        # 1. ヘッダーテキスト
        self.header_label = tk.Label(
            center_frame,
            text="こんにちは",
            font=self.font_header,
            bg=self.COLOR_BG,
            fg="#333333"
        )
        self.header_label.pack(pady=(0, 20))
        
        # 2. メインカード
        self.card_border = tk.Frame(center_frame, bg=self.COLOR_PRIMARY, padx=2, pady=2)
        self.card_border.pack(ipadx=0, ipady=0)
        
        self.card_inner = tk.Frame(self.card_border, bg=self.COLOR_WHITE, width=300, height=350)
        self.card_inner.pack()
        self.card_inner.pack_propagate(False)
        
        # === タブエリア ===
        tabs_frame = tk.Frame(self.card_inner, height=40, bg=self.COLOR_PRIMARY)
        tabs_frame.pack(fill="x", side="top")
        tabs_frame.pack_propagate(False)

        self.tab_login = tk.Label(
            tabs_frame, text="ログイン", font=self.font_tab,
            cursor="hand2"
        )
        self.tab_login.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.tab_login.bind("<Button-1>", lambda e: self._switch_to_login())

        self.tab_signup = tk.Label(
            tabs_frame, text="新規登録", font=self.font_tab,
            cursor="hand2"
        )
        self.tab_signup.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        self.tab_signup.bind("<Button-1>", lambda e: self._switch_to_signup())
        
        # === フォームエリア ===
        form_frame = tk.Frame(self.card_inner, bg=self.COLOR_WHITE)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ログインID
        tk.Label(form_frame, text="ログインID", font=self.font_label, fg=self.COLOR_PRIMARY, bg=self.COLOR_WHITE, anchor="w").pack(fill="x", pady=(10, 5))
        
        self.entry_id = tk.Entry(
            form_frame, textvariable=self.login_id_var,
            font=("Arial", 11), bd=1, relief="solid",
            validate="key", validatecommand=vcmd  # バリデーション設定
        )
        self.entry_id.pack(fill="x", ipady=3)
        
        # パスワード
        tk.Label(form_frame, text="パスワード", font=self.font_label, fg=self.COLOR_PRIMARY, bg=self.COLOR_WHITE, anchor="w").pack(fill="x", pady=(15, 5))
        
        self.entry_pass = tk.Entry(
            form_frame, textvariable=self.password_var, show="●",
            font=("Arial", 11), bd=1, relief="solid",
            validate="key", validatecommand=vcmd  # バリデーション設定
        )
        self.entry_pass.pack(fill="x", ipady=3)
        
        # アクションボタン
        tk.Frame(form_frame, bg=self.COLOR_WHITE, height=30).pack()
        
        self.btn_action = tk.Button(
            form_frame,
            text="ログインする",
            font=("Yu Gothic UI", 12, "bold"),
            cursor="hand2",
            relief="flat",
            command=self._on_action
        )
        self.btn_action.pack(fill="x", ipady=5)
        
        # 初期描画
        self._update_display()
        
        lbl_reset = tk.Label(
            form_frame, 
            text="パスワードを忘れた場合", 
            font=("Yu Gothic UI", 9, "underline"), 
            bg=self.COLOR_WHITE, 
            fg="#777", 
            cursor="hand2"
        )
        lbl_reset.pack(pady=(10, 0))
        lbl_reset.bind("<Button-1>", lambda e: self.controller.go_to_reset())
        
        # 初期描画
        self._update_display()
        
        # 戻るリンク
        lbl_back = tk.Label(center_frame, text="ホームに戻る", font=("Yu Gothic UI", 9), bg=self.COLOR_BG, fg="#777", cursor="hand2")
        lbl_back.pack(pady=15)
        lbl_back.bind("<Button-1>", lambda e: self.controller.go_to_home())

    def _switch_to_login(self):
        if not self.is_login_mode:
            self.is_login_mode = True
            self._update_display()

    def _switch_to_signup(self):
        if self.is_login_mode:
            self.is_login_mode = False
            self._update_display()

    def _update_display(self):
        if self.is_login_mode:
            self.header_label.config(text="こんにちは")
            self.tab_login.config(bg=self.COLOR_WHITE, fg=self.COLOR_PRIMARY)
            self.tab_signup.config(bg=self.COLOR_PRIMARY, fg=self.COLOR_WHITE)
            self.btn_action.config(
                text="ログインする",
                bg=self.COLOR_PRIMARY,
                fg=self.COLOR_WHITE,
                bd=0
            )
        else:
            self.header_label.config(text="初めまして")
            self.tab_login.config(bg=self.COLOR_PRIMARY, fg=self.COLOR_WHITE)
            self.tab_signup.config(bg=self.COLOR_WHITE, fg=self.COLOR_PRIMARY)
            self.btn_action.config(
                text="新規登録する",
                bg=self.COLOR_WHITE,
                fg=self.COLOR_PRIMARY,
                bd=1,
                relief="solid"
            )

    def _on_action(self):
        user_id = self.login_id_var.get()
        password = self.password_var.get()
        
        if self.is_login_mode:
            self.controller.login(user_id, password)
        else:
            self.controller.signup(user_id, password)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()