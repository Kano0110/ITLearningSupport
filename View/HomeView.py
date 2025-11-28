# HomeView.py

import tkinter as tk
from tkinter import ttk

class HomeView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("HOME")
        self.controller = controller  # MainControllerへの参照

        self._create_widgets()
        self.pack(expand=True, fill='both')

    def _create_widgets(self):
        # ラベル
        label = ttk.Label(self, text="HOME", font=('Arial', 24))
        label.pack(padx=20, pady=40)

        # 単語一覧ボタン（上から1番目）
        wordlist_button = ttk.Button(self, text="単語一覧",
                                command=self.controller.go_to_wordlist)
        wordlist_button.pack(pady=10, ipadx=20)

        # 問題を解くボタン（上から2番目）
        quiz_button = ttk.Button(self, text="問題を解く",
                                command=self.controller.go_to_quiz)
        quiz_button.pack(pady=10, ipadx=20)