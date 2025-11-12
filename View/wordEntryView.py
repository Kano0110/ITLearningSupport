# View/WordEntryView.py
import tkinter as tk
from tkinter import ttk, messagebox

class WordEntryView:
    """単語登録画面の View。controller を受け取り、ボタン操作は controller のメソッドを呼ぶ。"""

    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        # ここでは frame を持たせて pack/forget をコントローラから呼べるようにする
        self.frame = ttk.Frame(self.root)
        self.entry_Name = tk.Text(self.frame, width=40, height=1)
        self.entry_Kai = tk.Text(self.frame, width=40, height=10)
        self.cb_Category = ttk.Combobox(self.frame, values=[], width=17)
        self.cb_Bunya = ttk.Combobox(self.frame, values=[], width=17)
        self._build_ui()


    def _build_ui(self):
        self.root.title("単語登録")
        ttk.Label(self.frame, text='単語名：').place(x=60, y=30)
        self.entry_Name.place(x=150, y=30)
        ttk.Label(self.frame, text='解説：').place(x=65, y=120)
        self.entry_Kai.place(x=150, y=60)
        ttk.Label(self.frame, text='カテゴリ').place(x=70, y=220)
        self.cb_Category.place(x=120, y=220)
        ttk.Label(self.frame, text='分野').place(x=300, y=220)
        self.cb_Bunya.place(x=350, y=220)
        ttk.Button(self.frame, text='戻る', command=lambda: self.controller.create_close_window()).place(x=40, y=340)
        ttk.Button(self.frame, text='リセット', command=lambda: self.controller.create_reset_window()).place(x=250, y=340)
        ttk.Button(self.frame, text='作成', command=lambda: self.controller.get_id_pass()).place(x=490, y=340)

    def show(self):
        """この View を表示する（controller.show から呼ばれる）。"""
        self.frame.pack(expand=True, fill='both')

    def close(self):
        """表示を閉じる（pack_forget）。"""
        self.frame.pack_forget()

    def get_name(self):
        return self.entry_Name.get("1.0", tk.END).strip()

    def get_explain(self):
        return self.entry_Kai.get("1.0", tk.END).strip()

    def get_category(self):
        return self.cb_Category.get()

    def get_maker(self):
        return self.cb_Bunya.get()

    def clear_inputs(self):
        """入力欄をクリアする（リセット処理）。"""
        self.entry_Name.delete("1.0", tk.END)
        self.entry_Kai.delete("1.0", tk.END)
        self.cb_Category.set("")
        self.cb_Bunya.set("")

    def show_error(self, msg: str):
        messagebox.showerror("エラー", msg)

    def show_success(self, msg: str):
        messagebox.showinfo("完了", msg)