# AppController.py

import tkinter as tk
from Controller.HomeController import HomeController
from Controller.WordbookController import WordbookController

# WordbookControllerが使用するModelをインポート
from Model.WordbookModel import WordbookModel

class AppController:
    """アプリケーション全体の画面遷移を統括するメインコントローラー"""
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400") # ウィンドウサイズを設定

        # 状態: 現在表示されているコントローラー
        self.current_controller = None

        # 全てのコントローラーとモデルを初期化
        # ModelはWordbookControllerでのみ使用
        self.wordbook_model = WordbookModel()
       
        # 画面コントローラーの辞書
        self.controllers = {
            "home": HomeController(self),
            # WordbookControllerには、自身 (AppController) と共有Modelを渡す
            "wordbook": WordbookController(self, self.wordbook_model),
            # 他のコントローラーもここに追加...
            "create": None,
            "quiz": None
        }

        # 最初の画面を表示
        self.switch_view("home")

    def switch_view(self, view_name):
        """指定されたビューに切り替える"""
        if view_name not in self.controllers:
            print(f"Error: View '{view_name}' is not yet implemented.")
            return

        next_controller = self.controllers[view_name]

        # 1. 現在のビューを非表示にする
        if self.current_controller:
            self.current_controller.hide()

        # 2. 次のビューを表示し、それを現在のビューとして設定する
        self.current_controller = next_controller
        self.current_controller.show()
       
        # タイトルも更新
        self.root.title(f"WordBook - {view_name.capitalize()}")
       
        # (単語帳画面へ切り替える際に、WordbookControllerの初期データロードを再実行しても良い)
        if view_name == "wordbook":
             # WordbookControllerが初期データ（ID 1）を再ロードするロジックを呼ぶ
             self.controllers["wordbook"].initialize_data_on_switch()