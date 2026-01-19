# View/ResetView.py
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox

class ResetView(tk.Frame):
    """
    パスワードリセット画面 View
    デザインはAuthViewと統一
    """
    
    COLOR_PRIMARY = "#2C8CBE"
    COLOR_BG = "#F5F5F5"
    COLOR_WHITE = "#FFFFFF"
    
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(bg=self.COLOR_BG)
        
        self.login_id_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        
        # フォント設定
        self.font_header = tkfont.Font(family="Yu Gothic UI", size=20, weight="bold")
        self.font_label = tkfont.Font(family="Yu Gothic UI", size=11, weight="bold")
        
        # UI状態管理 (Step 1: ID入力, Step 2: PW入力)
        self.is_step_two = False
        
        self._create_ui()

    def _validate_ascii(self, P):
        """ASCIIチェック (AuthViewと共通)"""
        if P == "": return True
        if not P.isascii():
            messagebox.showwarning("入力エラー", "半角英数字のみ入力可能です。", parent=self)
            return False
        return True

    def _create_ui(self):
        # バリデーション
        vcmd = (self.register(self._validate_ascii), '%P')

        # センターフレーム
        center_frame = tk.Frame(self, bg=self.COLOR_BG)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # ヘッダー
        tk.Label(center_frame, text="パスワード再設定", font=self.font_header, bg=self.COLOR_BG, fg="#333333").pack(pady=(0, 20))
        
        # カード枠
        card_border = tk.Frame(center_frame, bg=self.COLOR_PRIMARY, padx=2, pady=2)
        card_border.pack(ipadx=0, ipady=0)
        
        # カード内部
        self.card_inner = tk.Frame(card_border, bg=self.COLOR_WHITE, width=300, height=350)
        self.card_inner.pack()
        self.card_inner.pack_propagate(False)
        
        # フォームエリア
        form_frame = tk.Frame(self.card_inner, bg=self.COLOR_WHITE)
        form_frame.pack(fill="both", expand=True, padx=20, pady=30)
        
        # --- Step 1: ID入力エリア ---
        self.step1_frame = tk.Frame(form_frame, bg=self.COLOR_WHITE)
        self.step1_frame.pack(fill="x", pady=10)
        
        tk.Label(self.step1_frame, text="ログインIDを入力してください", font=("Yu Gothic UI", 10), bg=self.COLOR_WHITE).pack(anchor="w", pady=(0, 10))
        
        tk.Label(self.step1_frame, text="ログインID", font=self.font_label, fg=self.COLOR_PRIMARY, bg=self.COLOR_WHITE, anchor="w").pack(fill="x")
        self.entry_id = tk.Entry(self.step1_frame, textvariable=self.login_id_var, font=("Arial", 11), bd=1, relief="solid", validate="key", validatecommand=vcmd)
        self.entry_id.pack(fill="x", ipady=3, pady=(5, 20))
        
        self.btn_check = tk.Button(self.step1_frame, text="次へ", font=("Yu Gothic UI", 12, "bold"), bg=self.COLOR_PRIMARY, fg=self.COLOR_WHITE, relief="flat", cursor="hand2", command=self._on_check_user)
        self.btn_check.pack(fill="x", ipady=5)

        # --- Step 2: PW入力エリア (初期非表示) ---
        self.step2_frame = tk.Frame(form_frame, bg=self.COLOR_WHITE)
        # packは後で行う
        
        tk.Label(self.step2_frame, text="新しいパスワードを入力してください", font=("Yu Gothic UI", 10), bg=self.COLOR_WHITE).pack(anchor="w", pady=(0, 10))

        tk.Label(self.step2_frame, text="新しいパスワード", font=self.font_label, fg=self.COLOR_PRIMARY, bg=self.COLOR_WHITE, anchor="w").pack(fill="x")
        self.entry_pass = tk.Entry(self.step2_frame, textvariable=self.new_password_var, show="●", font=("Arial", 11), bd=1, relief="solid", validate="key", validatecommand=vcmd)
        self.entry_pass.pack(fill="x", ipady=3, pady=(5, 20))
        
        self.btn_update = tk.Button(self.step2_frame, text="変更を保存", font=("Yu Gothic UI", 12, "bold"), bg=self.COLOR_PRIMARY, fg=self.COLOR_WHITE, relief="flat", cursor="hand2", command=self._on_update_password)
        self.btn_update.pack(fill="x", ipady=5)
        
        # 戻るボタン
        tk.Label(center_frame, text="キャンセルして戻る", font=("Yu Gothic UI", 9), bg=self.COLOR_BG, fg="#777", cursor="hand2").pack(pady=15)
        center_frame.bind("<Button-1>", lambda e: self.controller.show_login()) # 戻る処理

    def _on_check_user(self):
        login_id = self.login_id_var.get()
        self.controller.check_reset_user(login_id)

    def _on_update_password(self):
        login_id = self.login_id_var.get()
        new_pass = self.new_password_var.get()
        self.controller.perform_reset(login_id, new_pass)

    def show_step_two(self):
        """ID確認成功後にパスワード入力画面へ切り替え"""
        self.step1_frame.pack_forget()
        self.step2_frame.pack(fill="x", pady=10)
        self.entry_id.config(state="disabled") # IDを変更不可に

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()