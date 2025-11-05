# インポート
from tkinter import *
from tkinter import ttk
import tkinter


 
# 変数

category = ""
maker = ["松下", "日立", "東芝", "ソニー", "シャープ"]
maker2 = ["三井", "三菱", "住友", "安田"]

# 関数定義

# 入力された情報をどうする
def get_id_pass():
    name = entry_Name.get()
    Expla = entry_Kai.get()

    print('単語名：',name)
    print('解説：',Expla)
    print('カテゴリ：',cb_Category)
    print('分野：',cb_Bunya)

# リセット動作
def set_clear():
    entry_Name.delete("1.0", tkinter.END)
    entry_Kai.delete("1.0", tkinter.END)
    cb_Category.set(" ")
    cb_Bunya.set(" ")

# 戻るボタンの確認動作
def create_close_window():
     #新規ウィンドウを表示
     clo_win = tkinter.Toplevel(main_win)
     clo_win.title("戻る")
     clo_win.geometry("+660+350")
     clo_win.grab_set()

     label_sub_kakunin = ttk.Label(clo_win,text="本当に戻りますか？")

    # ボタン
     button_erase = ttk.Button(clo_win,text="はい",command=quit)
     button_return = ttk.Button(clo_win,text="いいえ",command=lambda:close_cloWindow())

    # 各種配置
     label_sub_kakunin.grid(row=3,column=2)
     button_erase.grid(row=5,column=3)
     button_return.grid(row=5,column=1)

    # サブウインドウを閉じる
     def close_cloWindow():
      clo_win.destroy()

# リセットボタンの確認動作
def create_reset_window():
    # 新規ウィンドウを表示
    sub_win = tkinter.Toplevel(main_win)
    sub_win.title("リセット確認")
    sub_win.geometry("+660+350")
    # 前ウィンドウを操作不能
    sub_win.grab_set()

    label_sub_kakunin = ttk.Label(sub_win,text="本当にリセットしますか？")

    # ボタン
    button_erase = ttk.Button(sub_win,text="はい",command=lambda:run_reset())
    button_return = ttk.Button(sub_win,text="いいえ",command=lambda:close_subWindow())

    # 各種配置
    label_sub_kakunin.grid(row=3,column=2)
    button_erase.grid(row=5,column=3)
    button_return.grid(row=5,column=1)

    # サブウインドウを閉じる
    def close_subWindow():
            sub_win.destroy()

    # リセットの上サブウインドウ閉じる
    def run_reset():
         set_clear()
         close_subWindow()


# メインウィンドウ
main_win = Tk()
main_win.title("単語登録")
main_win.geometry("700x300+400+250")




# 各要素

# いっちゃん上

label = ttk.Label(
    main_win,
    text = 'Hello World',
    foreground = "#000000",
    )
    
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
cb_Category = ttk.Combobox(main_win, textvariable=v, values=maker, width=17)
cb_Category.set("")

# 分野選択ボックス
label_Bunya = ttk.Label(main_win, text='分野')
v2 = StringVar()
cb_Bunya = ttk.Combobox(main_win, textvariable=v2, values=maker2, width=17)
cb_Bunya.set("")


#　ボタンの動作
button_quit = ttk.Button(main_win,text = '戻る',command=lambda:create_close_window())
button_reset = ttk.Button(main_win,text = 'リセット',command=lambda:create_reset_window())
button_sousin = ttk.Button(main_win,text = '作成',command=lambda:get_id_pass())





#　メインレイアウト
#入力欄およびラベル
label_Name.grid(row=1,column=0)
entry_Name.grid(row=1,column=1)
label_Kai.grid(row=2,column=0)
entry_Kai.grid(row=2,column=1)


#ボックスリスト
label_Catrgory.grid(row=4, column=0)
cb_Category.grid(row=4, column=1)
label_Bunya.grid(row=4, column=2)
cb_Bunya.grid(row=4, column=3)


#各種ボタン
button_quit.grid(row=5,column=0)
button_reset.grid(row=5,column=1)
button_sousin.grid(row=5,column=2)






main_win.mainloop()