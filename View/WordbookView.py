import tkinter as tk
from tkinter import ttk

Wordbook = tk.Tk()
Wordbook.title("WordBookPage")

wordID = "1"
wordName = "ベルクマンの法則"
wordText = "恒温動物においては、同じ種でも寒冷な地域に生息するものほど体重が大きく、近縁な種間では大型の種ほど寒冷な地域に生息する、という法則。\n類似のものにアレンの法則というものがあり、こちらは寒冷地ほど表面積が小さくなるというものである。"

label1 = ttk.Label(Wordbook, text=wordName)

label2 = ttk.Label(Wordbook, text=wordText)

backpage = ttk.Button(Wordbook, text="前のページへ")
nextpage = ttk.Button(Wordbook, text="次のページへ")
gohome = ttk.Button(Wordbook, text="homeへ戻る")

label1.pack(pady=10)
label2.pack(padx=(20,20),pady=(20,20))

backpage.pack(side=tk.LEFT,padx=10,pady=10)
nextpage.pack(side=tk.RIGHT,padx=10,pady=10)
gohome.pack(pady=10)

Wordbook.mainloop()