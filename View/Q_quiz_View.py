#Q_quiz_view.py

import tkinter as tk
from tkinter import ttk

class Q_Quiz_View(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        for i in range(10):
            self.rowconfigure(i, weight=1)

        # タイトル（上部中央）
        self.question_label = ttk.Label(self, text="", font=("TkDefaultFont", 12, "bold"))
        self.question_label.grid(row=0, column=0, columnspan=2, pady=(10, 4), sticky="n")

        # タグ・カテゴリ（右上）
        self.meta_label = ttk.Label(self, text="", font=("TkDefaultFont", 10), anchor="e")
        self.meta_label.grid(row=0, column=2, padx=(0, 10), sticky="ne")

        # 問題文（中央）
        self.display_area = ttk.Label(self, text="", font=("TkDefaultFont", 14, "bold"), wraplength=500)
        self.display_area.grid(row=2, column=0, columnspan=3, pady=(10, 4), sticky="n")

        # 隠された部分（中央下）
        self.hidden_area = ttk.Label(self, text="？？？", font=("TkDefaultFont", 12, "bold"), foreground="blue")
        self.hidden_area.grid(row=3, column=0, columnspan=3, pady=(0, 12), sticky="n")

        # 選択肢（縦並び）
        self.choice_frame = ttk.Frame(self)
        self.choice_frame.grid(row=4, column=0, columnspan=3, pady=(4, 12))

        # 結果表示
        self.result_label = ttk.Label(self, text="", font=("TkDefaultFont", 12))
        self.result_label.grid(row=5, column=0, columnspan=3, pady=(4, 8))

        # 列幅を均等にする
        for col in range(2):
            self.columnconfigure(col, weight=1)

        # ボタン配置
        self.finish_btn = ttk.Button(self, text="回答を終了する", command=self.controller.finish_quiz)
        self.finish_btn.grid(row=6, column=0, padx=12, pady=(4, 12), sticky="e")

        self.next_btn = ttk.Button(self, text="次の問題へ", command=self.controller.next_question)
        self.next_btn.grid(row=6, column=2, padx=12, pady=(4, 12), sticky="w")


    def show(self):
        self.pack(fill='both', expand=True)

    def hide(self):
        self.pack_forget()

    def display_question(self, index, total, term, choices, mode, tag=None, category=None):
        self.clear_ui()
        self.question_label.config(text=f"{index}問目 / {total}問中")

        meta_parts = []
        if category:
            meta_parts.append(f"カテゴリ: {category}")
        if tag:
            meta_parts.append(f"タグ: {tag}")
        self.meta_label.config(text=" / ".join(meta_parts))

        if mode == "hide_word":
            self.display_area.config(text=term.get("desc", ""))
            self.hidden_area.config(text="？？？")
        elif mode == "hide_explanation":
            self.display_area.config(text=term.get("name", ""))
            self.hidden_area.config(text="？？？")
        else:
            self.display_area.config(text="（不明な出題形式）")
            self.hidden_area.config(text="？？？")

        labels = ["ア", "イ", "ウ", "エ"]
        for i, choice in enumerate(choices):
            text = choice.get("name") if mode == "hide_word" else choice.get("desc")
            btn = ttk.Button(self.choice_frame, text=f"{labels[i]}　{text}",
                            command=lambda c=choice: self.controller.handle_answer(c))
            btn.pack(anchor='w', pady=4, padx=12)

    def show_result(self, is_correct, correct_term):
        """回答後の正誤表示と隠された部分の表示"""
        self.result_label.config(
            text="正解！" if is_correct else "残念…",
            foreground="green" if is_correct else "red"
        )

        # 隠されていた部分を表示
        if self.controller.mode == "hide_word":
            self.hidden_area.config(text=correct_term.get("name", ""))
        else:
            self.hidden_area.config(text=correct_term.get("desc", ""))

        # 選択肢を非表示
        for child in self.choice_frame.winfo_children():
            child.pack_forget()

        # 次へ／終了ボタンを表示（← ループの外に出す）
        self.next_btn.grid()
        self.finish_btn.grid()

    def clear_ui(self):
        """前問のUIを初期化"""
        self.result_label.config(text="")
        self.hidden_area.config(text="？？？")
        for child in self.choice_frame.winfo_children():
            child.destroy()
        self.next_btn.grid_remove()
        self.finish_btn.grid_remove()
