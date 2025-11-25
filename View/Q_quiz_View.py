#Q_quiz_view.py

import tkinter as tk
from tkinter import ttk

class Q_Quiz_View(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.pack(fill='both', expand=True)

        self.question_label = ttk.Label(self, text="", font=("TkDefaultFont", 12, "bold"))
        self.question_label.pack(pady=(10, 4))

        self.meta_label = ttk.Label(self, text="", foreground="gray")
        self.meta_label.pack(pady=(0, 8))

        self.display_area = ttk.Label(self, text="", wraplength=500, font=("TkDefaultFont", 11))
        self.display_area.pack(pady=(4, 12))

        self.hidden_area = ttk.Label(self, text="？？？", font=("TkDefaultFont", 12, "bold"), foreground="blue")
        self.hidden_area.pack(pady=(0, 12))

        self.choice_frame = ttk.Frame(self)
        self.choice_frame.pack(pady=(4, 12))

        self.result_label = ttk.Label(self, text="", font=("TkDefaultFont", 12))
        self.result_label.pack(pady=(4, 8))

        self.next_btn = ttk.Button(self, text="次の問題へ", command=self.controller.next_question)
        self.next_btn.pack(side=tk.RIGHT, padx=12, pady=(4, 12))
        self.next_btn.pack_forget()

        self.finish_btn = ttk.Button(self, text="回答を終了する", command=self.controller.finish_quiz)
        self.finish_btn.pack(side=tk.LEFT, padx=12, pady=(4, 12))
        self.finish_btn.pack_forget()

    def show(self):
        self.pack(fill='both', expand=True)

    def hide(self):
        self.pack_forget()

    def display_question(self, index, total, term, choices, mode, tag=None, category=None):
        """1問分の表示を行う"""
        self.clear_ui()

        self.question_label.config(text=f"{index}問目 / {total}問中")
        meta = []
        if category:
            meta.append(f"カテゴリ：{category}")
        if tag:
            meta.append(f"タグ：{tag}")
        self.meta_label.config(text=" / ".join(meta))

        # 表示する部分と隠す部分を決定
        if mode == "hide_word":
            self.display_area.config(text=term.get("desc", ""))
            self.hidden_area.config(text="？？？")
        else:
            self.display_area.config(text=term.get("name", ""))
            self.hidden_area.config(text="？？？")

        # 選択肢ボタン生成
        labels = ["ア", "イ", "ウ", "エ"]
        for i, choice in enumerate(choices):
            if mode == "hide_word":
                text = choice.get("name", "")
            else:
                text = choice.get("desc", "")
            btn = ttk.Button(self.choice_frame, text=f"{labels[i]}　{text}",
                             command=lambda c=choice: self.controller.handle_answer(c))
            btn.pack(anchor='w', pady=4, padx=12)

    def show_result(self, is_correct, correct_term):
        """回答後の正誤表示と隠された部分の表示"""
        self.result_label.config(text="正解！" if is_correct else "残念…", foreground="green" if is_correct else "red")

        # 隠されていた部分を表示
        if self.controller.mode == "hide_word":
            self.hidden_area.config(text=correct_term.get("name", ""))
        else:
            self.hidden_area.config(text=correct_term.get("desc", ""))

        # 選択肢を非表示
        for child in self.choice_frame.winfo_children():
            child.pack_forget()

        # 次へ／終了ボタンを表示
        self.next_btn.pack(side=tk.RIGHT, padx=12, pady=(4, 12))
        self.finish_btn.pack(side=tk.LEFT, padx=12, pady=(4, 12))

    def clear_ui(self):
        """前問のUIを初期化"""
        self.result_label.config(text="")
        self.hidden_area.config(text="？？？")
        for child in self.choice_frame.winfo_children():
            child.destroy()
        self.next_btn.pack_forget()
        self.finish_btn.pack_forget()
