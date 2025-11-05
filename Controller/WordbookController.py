# WordbookController.py

import tkinter as tk
# パスの修正: フォルダ名.ファイル名からクラスをインポートする
from Model.WordbookModel import WordbookModel 
from View.WordbookView import WordbookView 

class AppController:
    def __init__(self, root):
        self.root = root
        # クラス名をWordbookModelに変更
        self.model = WordbookModel() 
        self.view = WordbookView(root, self) 

        # アプリ起動時の初期データロード
        self.model.fetch_word_data()
        self.view.update_data(self.model.wN, self.model.wD)

    # --- UI表示・非表示トグルロジック ---
    
    def toggle_name_view(self):
        """名前表示/非表示ボタンが押されたときの処理"""
        # 1. Viewの現在の状態を反転
        new_state = not self.view.name_is_visible 
        
        # 2. Viewに新しい状態と現在のデータを渡して更新を指示
        self.view.toggle_name_display(new_state, self.model.wN)

    def toggle_description_view(self):
        """説明文表示/非表示ボタンが押されたときの処理"""
        new_state = not self.view.desc_is_visible 
        self.view.toggle_description_display(new_state, self.model.wD)

    # --- データ切り替えロジック (次へ/前へ) ---
    
    def handle_next_word(self):
        """次の単語へ移動する処理"""
        # 1. Modelに状態変更を指示
        self.model.go_to_next_word()
        
        # 2. ViewをModelの最新データで更新
        self.view.update_data(self.model.wN, self.model.wD)

    def handle_previous_word(self):
        """前の単語へ移動する処理"""
        # 1. Modelに状態変更を指示
        self.model.go_to_previous_word()
        
        # 2. ViewをModelの最新データで更新
        self.view.update_data(self.model.wN, self.model.wD)
        
    # --- 画面遷移プレースホルダー (担当外のページ) ---
    
    def handle_go_home(self):
        """Homeへ戻るボタンが押されたときの処理"""
        print("Controller: Home画面への遷移を指示します。")
        print("【連携待ち】: 担当者にHome画面への遷移を依頼してください。")

    def handle_go_word_list(self):
        """単語一覧へ戻るボタンが押されたときの処理"""
        print("Controller: 単語一覧画面への遷移を指示します。")
        print("【連携待ち】: 担当者に単語一覧画面への遷移を依頼してください。")


# --- メイン実行部 ---
#if __name__ == "__main__":
    # Tkinterのルートウィンドウを設定
#    root = tk.Tk()
#    app = AppController(root)
#    root.mainloop()