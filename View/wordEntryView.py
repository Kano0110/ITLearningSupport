# インポート
from tkinter import *
from tkinter import ttk
import tkinter

from Model.wordEntryModel import wordEntry
from Controller.wordEntryCont import wordEntry


# メインウィンドウ
main_win = Tk()
main_win.title("単語登録")
main_win.geometry("700x300+400+250")


# いっちゃん上


    
# 単語名入力
label_Name = ttk.Label(main_win, text='単語名：')
entry_Name = tkinter.Text(main_win, 
                      width=40,
                      height=1)

# 単語の解説
label_Kai = ttk.Label(main_win, text='解説：')
entry_Kai = tkinter.Text(main_win, 
                     width=40,
                     height=10)




# カテゴリ選択ボックス
label_Catrgory = ttk.Label(main_win, text='カテゴリ')
v = StringVar()
cb_Category = ttk.Combobox(main_win, textvariable=v, values=wordEntry.maker, width=17)
cb_Category.set("")

# 分野選択ボックス
label_Bunya = ttk.Label(main_win, text='分野')
v2 = StringVar()
cb_Bunya = ttk.Combobox(main_win, textvariable=v2, values=wordEntry.maker2, width=17)
cb_Bunya.set("")


#　ボタンの動作
button_quit = ttk.Button(main_win,text = '戻る',command=lambda:wordEntry.create_close_window())
button_reset = ttk.Button(main_win,text = 'リセット',command=lambda:wordEntry.create_reset_window())
button_sousin = ttk.Button(main_win,text = '作成',command=lambda:wordEntry.get_id_pass())





#　メインレイアウト
#入力欄およびラベル
label_Name.grid(row=2,column=2)
entry_Name.grid(row=2,column=3)
label_Kai.grid(row=3,column=2)
entry_Kai.grid(row=3,column=3)


#ボックスリスト
label_Catrgory.grid(row=5, column=1)
cb_Category.grid(row=5, column=2)
label_Bunya.grid(row=5, column=3)
cb_Bunya.grid(row=5, column=4)


#各種ボタン
button_quit.grid(row=10,column=2)
button_reset.grid(row=10,column=3)
button_sousin.grid(row=10,column=4)

    # 各種配置




sub_win = tkinter.Toplevel(main_win)
sub_win.title("リセット確認")
sub_win.geometry("+660+350")


label_sub_kakunin = ttk.Label(sub_win,text="本当にリセットしますか？")

    # ボタン
button_erase = ttk.Button(sub_win,text="はい",command=lambda:wordEntry.run_reset())
button_return = ttk.Button(sub_win,text="いいえ",command=lambda:wordEntry.close_subWindow())

    # 各種配置
label_sub_kakunin.grid(row=3,column=2)
button_erase.grid(row=5,column=3)
button_return.grid(row=5,column=1)

label_sub_kakunin.grid(row=3,column=2)
button_erase.grid(row=5,column=3)
button_return.grid(row=5,column=1)




main_win.mainloop()