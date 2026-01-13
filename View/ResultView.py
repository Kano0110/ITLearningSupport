# View/ResultView.py
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
 
class ResultView:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.frame = ttk.Frame(self.root)
        self.scrollbar_frame = tk.Frame(self.frame)
 
        # ラベル保持用
        self.labelCorrect = None
        self.labelPercent = None
        self.listCategoryName = None
        self.listTagName = None
        self.listboxWrong = None
        self.labelTime = None
 
        self._build_ui()
 
    def _build_ui(self):
        self.root.title("結果発表")
 
        self.result_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        my_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        Wrong_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.Correct_font = tkfont.Font(family="Helvetica", size=15, weight="bold")
 
        # 正解数と正解率（初期は空）
        self.labelCorrect = ttk.Label(self.frame, text="", font=self.Correct_font)
        self.labelCorrect.place(x=60, y=40)
 
        self.labelPercent = ttk.Label(self.frame, text="", font=self.Correct_font)
        self.labelPercent.place(x=370, y=38)

        # 経過時間
        """まだ制作中"""
        self.labelTime = ttk.Label(self.frame, text="", font=self.Correct_font)
        self.labelTime.place(x=60, y=100)

 
        # 絞り込み条件
        labelframe = tk.LabelFrame(self.frame, text="絞り込み条件", labelanchor="n", width=300, height=100, font=my_font)
        labelframe.place(x=60, y=160)
 
        ttk.Label(labelframe, text='カテゴリ：').grid(row=0, column=0, padx=10, pady=5)
        self.listCategoryName = tk.Listbox(labelframe)
        self.listCategoryName.grid(row=1, column=1, padx=10, pady=5)
 
        ttk.Label(labelframe, text='タグ：').grid(row=0, column=1, padx=10, pady=5)
        self.listTagName = tk.Listbox(labelframe)
        self.listTagName.grid(row=1, column=0, padx=10, pady=5)
 
        # ボタン
        button_list = ttk.Button(self.frame, text='単語一覧に戻る', command=self.controller.return_wordlist)
        button_question = ttk.Button(self.frame, text='出題形式選択へ戻る', command=self.controller.return_qselect)
        button_again = ttk.Button(self.frame, text='同じ条件でもう一度解く', command=self.controller.redo_quiz)

        button_list.place(x=70, y=430)
        button_question.place(x=200, y=430)
        button_again.place(x=400, y=430)
 
        # 間違えた問題リスト
        labelWrong = ttk.Label(self.frame, text="間違えた問題", font=Wrong_font)
        labelWrong.place(x=380, y=160)
 
        self.listboxWrong = tk.Listbox(self.scrollbar_frame)
        self.scrollbar_frame.place(x=380, y=180)
        self.listboxWrong.pack(side=tk.LEFT)
 
        scroll_bar = tk.Scrollbar(self.scrollbar_frame, command=self.listboxWrong.yview)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listboxWrong.config(yscrollcommand=scroll_bar.set)
 
    def set_result(self, correct_count, total_questions, percent,category=None, tag=None, wronged=None, elapsed_time=None):
        self.labelCorrect.config(text=f"{total_questions}問中、{correct_count}問正解！")
        self.labelPercent.config(text=f"正解率：{percent}%")

        # カテゴリ
        self.listCategoryName.delete(0, tk.END)
        if category:
            for c in category:
                self.listCategoryName.insert(tk.END, c)
        else:
            self.listCategoryName.insert(tk.END, "N/A")

        # タグ
        self.listTagName.delete(0, tk.END)
        if tag:
            for t in tag:
                self.listTagName.insert(tk.END, t)
        else:
            self.listTagName.insert(tk.END, "N/A")

        # 経過時間
        if elapsed_time is not None:
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            self.labelTime.config(text=f"経過時間：{minutes}分{seconds}秒")
        else:
            self.labelTime.config(text="")

        # 間違えた問題リスト更新

        self.listboxWrong.delete(0, tk.END)
        if wronged:
            for item in wronged:
                self.listboxWrong.insert(tk.END, item)
  
    def show(self):
        self.frame.pack(expand=True, fill='both')
 
    def close(self):
        self.frame.pack_forget()