# WordbookView.py

import tkinter as tk
from tkinter import ttk

class WordbookView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("WordBookPage")
        self.controller = controller 
        
        # UI状態を管理するインスタンス変数 (Viewの責務)
        self.name_is_visible = True
        self.desc_is_visible = True

        # Tkinter変数 (StringVar) の定義
        self.wordName_var = tk.StringVar(value="") 
        self.wordDescription_var = tk.StringVar(value="")
        self.btnName_var = tk.StringVar(value="名前を隠す")
        self.btnDescription_var = tk.StringVar(value="説明を隠す")

        self._create_widgets()
        self.pack(expand=True, fill='both')

    def _create_widgets(self):
        # ラベル
        self.label1 = ttk.Label(self, textvariable=self.wordName_var)
        self.label2 = ttk.Label(self, textvariable=self.wordDescription_var, wraplength=400)

        # 表示/非表示トグルボタン
        self.visNameBTN = ttk.Button(self, textvariable=self.btnName_var, 
                                     command=self.controller.toggle_name_view)
        self.visDescriptionBTN = ttk.Button(self, textvariable=self.btnDescription_var, 
                                            command=self.controller.toggle_description_view)

        # 遷移ボタン (Controllerにイベントを委譲)
        self.backPageBTN = ttk.Button(self, text="前のページへ", command=self.controller.handle_previous_word)
        self.nextPageBTN = ttk.Button(self, text="次のページへ", command=self.controller.handle_next_word)
        self.goHomeBTN = ttk.Button(self, text="homeへ戻る", command=self.controller.handle_go_home)
        self.goListBTN = ttk.Button(self, text="単語一覧へ戻る", command=self.controller.handle_go_word_list) 

        # 実際に配置する
        self.label1.pack(pady=10)
        self.visNameBTN.pack(pady=(4,10))
        self.label2.pack(padx=(20,20),pady=(20,20))
        self.visDescriptionBTN.pack(pady=(4,20))

        self.backPageBTN.pack(side=tk.LEFT,padx=10,pady=10)
        self.nextPageBTN.pack(side=tk.RIGHT,padx=10,pady=10)
        self.goHomeBTN.pack(pady=(10, 5))
        self.goListBTN.pack(pady=(5, 10))
    
    # --- Controllerから呼び出されるメソッド ---
    
    def update_data(self, name, description):
        """Modelから取得したデータでViewを更新する"""
        
        # 名前ラベルの更新
        if self.name_is_visible:
            self.wordName_var.set(name)
            self.btnName_var.set("名前を隠す")
        else:
            # 非表示状態ならデータが更新されても "???" を維持
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")
            
        # 説明文ラベルの更新
        if self.desc_is_visible:
            self.wordDescription_var.set(description)
            self.btnDescription_var.set("説明を隠す")
        else:
            self.wordDescription_var.set("???")
            self.btnDescription_var.set("説明を見る")

    def toggle_name_display(self, is_visible, name):
        """名前の表示状態を切り替える (Controllerから呼ばれる)"""
        self.name_is_visible = is_visible
        
        if is_visible:
            self.wordName_var.set(name)
            self.btnName_var.set("名前を隠す")
        else:
            self.wordName_var.set("???")
            self.btnName_var.set("名前を見る")
            
    def toggle_description_display(self, is_visible, description):
        """説明文の表示状態を切り替える (Controllerから呼ばれる)"""
        self.desc_is_visible = is_visible
        
        if is_visible:
            self.wordDescription_var.set(description)
            self.btnDescription_var.set("説明を隠す")
        else:
            self.wordDescription_var.set("???")
            self.btnDescription_var.set("説明を見る")
