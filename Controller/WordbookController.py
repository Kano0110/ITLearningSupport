# WordbookController.py

import tkinter as tk
from Model.WordbookModel import WordbookModel
from View.WordbookView import WordbookView

class WordbookController:
    def __init__(self, root_controller, model):
        # root_controller: AppControllerへの参照
        self.root_controller = root_controller
        self.model = model
        self.view = WordbookView(root_controller.root, self)

        # アプリ起動時はデータをロードしない (AppControllerからの指示を待つため)
       
    def initialize_data_on_switch(self):
        """画面に切り替わったときに初期データ（ID 1）を強制的にロードする"""
        self.model.current_word_id = 1 # 常に最初の単語から始める
        self.model.fetch_word_data()
        self.view.update_data(self.model.wN, self.model.wD)

    def show(self):
        """この画面を表示状態にする"""
        self.view.pack(expand=True, fill='both')

    def hide(self):
        """この画面を非表示状態にする"""
        self.view.pack_forget()

    # --- UI表示・非表示トグルロジック ---
   
    def toggle_name_view(self):
        new_state = not self.view.name_is_visible
        self.view.toggle_name_display(new_state, self.model.wN)

    def toggle_description_view(self):
        new_state = not self.view.desc_is_visible
        self.view.toggle_description_display(new_state, self.model.wD)

    # --- データ切り替えロジック (次へ/前へ) ---
   
    def handle_next_word(self):
        self.model.go_to_next_word()
        self.view.update_data(self.model.wN, self.model.wD)

    def handle_previous_word(self):
        self.model.go_to_previous_word()
        self.view.update_data(self.model.wN, self.model.wD)
       
    # --- 画面遷移プレースホルダー (Homeへ/一覧へ) ---
   
    def handle_go_home(self):
        # Homeへの遷移はAppControllerに依頼
        self.root_controller.switch_view("home")

    def handle_go_word_list(self):
        # 単語一覧への遷移はAppControllerに依頼
        self.root_controller.switch_view("wordlist")