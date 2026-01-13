# View/WordEntryView.py
import tkinter as tk
from tkinter import ttk, messagebox

class WordEntryView:
    """単語登録画面の View。controller を受け取り、ボタン操作は controller のメソッドを呼ぶ。"""

    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        
        self.style = ttk.Style()
        # メインフレーム
        self.frame = ttk.Frame(self.root)

        vcmd = (self.frame.register(self._validate_hiragana), "%P")
        
        # ウィジェット定義
        self.entry_Name = ttk.Entry(self.frame, width=40, font=("Arial", 11))
        self.entry_Yomi = ttk.Entry(self.frame, width=40, validate="key", validatecommand=vcmd, font=("Arial", 11))
        
        self.entry_Kai = tk.Text(self.frame, width=30, height=5, font=("Arial", 11))
        
        # Combobox (state='normal' などの指定なし = デフォルトで入力も選択も可能)
        self.cb_Category = ttk.Combobox(self.frame, values=[], width=17, font=("Arial", 11))
        self.cb_Tag = ttk.Combobox(self.frame, values=[], width=17, font=("Arial", 11))
        
        # タイトルフレーム
        self.title_frame = tk.Frame(self.frame)
        
        self._build_ui()

    def _build_ui(self):
        # スタイル設定
        self.style.configure("Reset.TButton", foreground="#FF2200")
        # 作成ボタンを大きめのフォントと余白で強調
        self.style.configure("Create.TButton", foreground="#589D41", font=("Arial",11))
        self.style.configure("Back.TButton", foreground="#3F7FF5")

        # レイアウトを grid で構築し、リサイズに追従させる
        # タイトルフレーム（単語一覧と同じスタイル）
        title_frame = tk.Frame(self.frame, bg="#49AD28")
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 10))

        title_label = tk.Label(
            title_frame,
            text="単語登録",
            font=('Arial', 18, 'bold'),
            bg="#49AD28",
            fg='white'
        )
        title_label.pack(anchor='center', padx=40, pady=5)

        # グリッド構成: ラベル列(固定) + 入力列(伸縮) + 右側操作列(一部固定)
        self.frame.columnconfigure(0, weight=0, minsize=110)
        self.frame.columnconfigure(1, weight=1, minsize=200)
        self.frame.columnconfigure(2, weight=0, minsize=120)
        # 行の伸縮: 解説のテキストエリアが縦に伸びる
        self.frame.rowconfigure(3, weight=1)

        # 単語名
        ttk.Label(self.frame, text='単語名：', font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.entry_Name.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
        ttk.Button(self.frame, text='リセット', style="Reset.TButton", command=lambda: self.controller.create_reset_window()).grid(row=1, column=2, sticky="e", padx=20, pady=5)

        # ふりがな
        ttk.Label(self.frame, text='ふりがな：', font=("Arial", 11)).grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.entry_Yomi.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=5)

        # 解説
        ttk.Label(self.frame, text='解説：', font=("Arial", 11)).grid(row=3, column=0, sticky="nw", padx=20, pady=5)
        self.entry_Kai.grid(row=3, column=1, sticky="nsew", padx=(0, 10), pady=5)

        # カテゴリ / タグ 行
        ttk.Label(self.frame, text='カテゴリ', font=("Arial", 11)).grid(row=4, column=0, sticky="w", padx=20, pady=5)
        self.cb_Category.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=5)

        ttk.Label(self.frame, text='タグ', font=("Arial", 11)).grid(row=5, column=0, sticky="w", padx=20, pady=5)
        self.cb_Tag.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=5)

        # フッターボタン行
        ttk.Button(self.frame, text='単語一覧に戻る', command=lambda: self.controller.create_close_window(), style="Back.TButton").grid(row=6, column=0, sticky="e", padx=20, pady=(10, 20))
        ttk.Button(self.frame, text='作成', style="Create.TButton", command=lambda: self.controller.get_id_pass()).grid(row=6, column=2, sticky="e", padx=20, pady=(10, 20))

        self.entry_Name.bind("<Return>", lambda e: self.entry_Yomi.focus_set())
        self.entry_Yomi.bind("<Return>", lambda e: self.entry_Kai.focus_set())
        self.entry_Kai.bind("<Return>", lambda e: None)  # 最後は何もしない

    def show(self):
        """この View を表示する（controller.show から呼ばれる）。"""
        # AppControllerのサイズ(600x500)に合わせて fill する
        self.frame.pack(expand=True, fill='both')

    def close(self):
        """表示を閉じる（pack_forget）。"""
        self.frame.pack_forget()

    def set_combo_values(self, categories: list, tags: list):
        """プルダウンの候補を設定する"""
        self.cb_Category['values'] = categories
        self.cb_Tag['values'] = tags

    def get_name(self):
        return self.entry_Name.get().strip()
    
    def get_yomi(self):
        return self.entry_Yomi.get().strip()
    
    def get_explain(self):
        return self.entry_Kai.get("1.0", "end-1c").strip()

    def get_category(self):
        return self.cb_Category.get().strip()

    def get_tag(self):
        return self.cb_Tag.get().strip()
    
    def _validate_hiragana(self, P):
        # P = 入力後の文字列
        if P == "":
            return True
        import re
        return bool(re.fullmatch(r"[ぁ-ゖー]*", P))

    def clear_inputs(self):
        """入力欄をクリアする（リセット処理）。"""
        # ttk.Entry は .delete(0, tk.END) を使う
        self.entry_Name.delete(0, tk.END)
        self.entry_Yomi.delete(0, tk.END)
        # tk.Text は .delete("1.0", tk.END) を使う
        self.entry_Kai.delete("1.0", tk.END)
        self.cb_Category.set("")
        self.cb_Tag.set("")

    def show_error(self, msg: str):
        messagebox.showerror("エラー", msg)

    def show_success(self, msg: str):
        messagebox.showinfo("完了", msg)