# View/ResultView.py
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import math

class ResultView:

    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.style = ttk.Style()
        self.frame = ttk.Frame(self.root)
        self.scrollbar_frame = tk.Frame(root)

        ZanteiCategory = "ネットワーク"
        ZanteiTag = "絞り込みなし"
        total_questions = 10
        ZanteiSeikai = 8
        ZanteiPercent = 1500
        ZanteiWrong = ["DNS","HTTP/HTTPS"]

        self._build_ui()
#cd_Bunya

    def _build_ui(self):
        self.root.title("結果発表")

        """正解数と正解率"""
        QuestCount = self.string_num = str(self.total_questions)
        CorrectCount = self.string_num = str(self.ZanteiSeikai)


        ZanteiPercent = (self.ZanteiSeikai / self.total_questions) * 100
        ZanteiPercent = math.floor(ZanteiPercent)
        CorrectPerc = self.string_num = str(ZanteiPercent)

        labelCorrect = ttk.Label(self.root, text= QuestCount + "問中、" + CorrectCount + "問正解！",font=self.Correct_font) 
        labelCorrect.place(x=60,y=40)

        labelPercent = ttk.Label(self.root, text= "正解率：" + CorrectPerc + "%",font=self.Correct_font) 
        labelPercent.place(x=370,y=38)

        self.result_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        my_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        Wrong_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.Correct_font = tkfont.Font(family="Helvetica", size=15, weight="bold")

        """解答結果の部品"""
        labelframe = tk.LabelFrame(self.root, text="絞り込み条件",labelanchor="n",width=300,height=100,font=my_font)
        labelframe.place(x=60,y=100)

        label_Category = ttk.Label(labelframe, text='カテゴリ：') 
        label_Category.grid(row=0, column=0, padx=10, pady=5)
        label_CategoryName = tk.Label(labelframe, text=self.ZanteiCategory, bg = "#ffffff")
        label_CategoryName.grid(row=0, column=1, padx=10, pady=5)

        label_Tag = ttk.Label(labelframe, text='タグ：')
        label_Tag.grid(row=1, column=0, padx=10, pady=5)
        label_TagName = tk.Label(labelframe, text=self.ZanteiTag, bg = "#ffffff")
        label_TagName.grid(row=1, column=1, padx=10, pady=5)


        """各種ボタン"""
        button_list = ttk.Button(self.root,text = '単語一覧に戻る',command=lambda: self.controller.ReturnWordView())
        button_question = ttk.Button(self.root,text = '出題形式選択へ戻る',command=lambda: self.controller.ReturnFormatSellect())
        button_again = ttk.Button(self.root,text = '同じ条件でもう一度解く',command=lambda: self.controller.RedoQuestion())
        button_list.place(x=70, y=300) #
        button_question.place(x=70, y=350) #
        button_again.place(x=400, y=350) #

        """間違えた問題周辺の部品"""
        labelWrong = ttk.Label(self.root, text="間違えた問題",font=Wrong_font) 
        listboxWrong = tk.Listbox(self.scrollbar_frame)

        labelWrong.place(x=380, y=100)
        self.scrollbar_frame.place(x=380, y=120)

        for i in self.ZanteiWrong:
            listboxWrong.insert(tk.END, i)
        listboxWrong.pack(side=tk.LEFT)

        scroll_bar =tk.Scrollbar(self.scrollbar_frame, command=listboxWrong.yview)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        listboxWrong.config(yscrollcommand=scroll_bar.set)


    
    def show(self):
        """この View を表示する（controller.show から呼ばれる）。"""
        self.frame.pack(expand=True, fill='both')

    def close(self):
        """表示を閉じる（pack_forget）。"""
        self.frame.pack_forget()

