# HomeController.py

from View.HomeView import HomeView

class HomeController:
    """HomeViewからのイベントを受け取り、画面遷移を指示するControllerクラス"""
    def __init__(self, root_controller):
        # アプリケーション全体のメインコントローラーへの参照を保持
        self.root_controller = root_controller
        self.view = HomeView(root_controller.root, self)

    # --- 画面遷移ハンドラー ---

# HomeController.py の該当メソッド
    def go_to_wordentry(self):
        """「単語帳を作る」ボタンが押された時の処理"""
        print("Controller: 単語帳作成画面へ遷移を要求")
        self.root_controller.switch_view("wordentry")

    def go_to_wordlist(self):
        """「単語帳を見る」ボタンが押された時の処理 -> WordListへ遷移"""
        print("Controller: 単語一覧画面 (WordList) へ遷移を要求")
        # メインコントローラーを通じてWordList画面への切り替えを指示
        self.root_controller.switch_view("wordlist")

    #def go_to_quiz(self):
    #    """「問題を解く」ボタンが押された時の処理"""
    #    print("Controller: クイズ画面へ遷移を要求")
    #    self.root_controller.switch_view("quiz")
       
    def show(self):
        """この画面を表示状態にする"""
        self.view.pack(expand=True, fill='both')

    def hide(self):
        """この画面を非表示状態にする"""
        self.view.pack_forget()