# インポート
from tkinter import *
from tkinter import ttk
import tkinter

from Model.wordEntryModel import wordEntry
from View.wordEntryView import wordEntryView

#Contは動作の中継役
 
# 変数

category = ""
maker = ["松下", "日立", "東芝", "ソニー", "シャープ"]
maker2 = ["三井", "三菱", "住友", "安田"]

# 関数定義

# 入力された情報をどうする
def get_id_pass():

    Name = wordEntry.entry_Name.get("1.0", tkinter.END)
    Kai = wordEntry.entry_Kai.get("1.0", tkinter.END)

    print('単語名：',Name)
    print('解説：',Kai)
    print('カテゴリ：',wordEntry.cb_Category)
    print('分野：',wordEntry.cb_Bunya)

# リセット動作
def set_clear():
    wordEntryView.entry_Name.delete("1.0", tkinter.END)
    wordEntryView.entry_Kai.delete("1.0", tkinter.END)
    wordEntryView.cb_Category.set(" ")
    wordEntryView.cb_Bunya.set(" ")

# 戻るボタンの確認動作
def create_close_window():
     #新規ウィンドウを表示
     clo_win = tkinter.Toplevel(main_win)
     clo_win.title("戻る")
     clo_win.geometry("+660+350")
     clo_win.grab_set()

     wordEntryView.label_sub_kakunin = ttk.Label(clo_win,text="本当に戻りますか？")

    # ボタン
     wordEntryView.button_erase = ttk.Button(clo_win,text="はい",command=quit)
     wordEntryView.button_return = ttk.Button(clo_win,text="いいえ",command=lambda:close_cloWindow())



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

    wordEntry.label_sub_kakunin = ttk.Label(sub_win,text="本当にリセットしますか？")

    # ボタン
    wordEntry.button_erase = ttk.Button(sub_win,text="はい",command=lambda:run_reset())
    wordEntry.button_return = ttk.Button(sub_win,text="いいえ",command=lambda:close_subWindow())


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





main_win.mainloop()