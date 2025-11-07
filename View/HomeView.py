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

        # 単語帳を作るボタン (遷移1)
        # wordentryへ遷移
        create_button = ttk.Button(self, text="単語帳を作る", 
                                   command=self.controller.go_to_wordentry)
        create_button.pack(pady=10, ipadx=20)

        # 単語帳を見るボタン (遷移2)
        # wordlistへ遷移
        view_button = ttk.Button(self, text="単語帳を見る", 
                                 command=self.controller.go_to_wordlist)
        view_button.pack(pady=10, ipadx=20)

        # 問題を解くボタン (遷移3)
       # solve_button = ttk.Button(self, text="問題を解く", 
       #                          command=self.controller.go_to_quiz)
       # solve_button.pack(pady=10, ipadx=20)