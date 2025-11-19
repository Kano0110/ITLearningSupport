# Controller/AppController.py
import traceback#デバッグ用

class AppController:
    """アプリケーション全体の画面遷移を統括するメインコントローラー"""
    def __init__(self, root, db_path=None):
        self.root = root
        self.root.geometry("600x400")
        self.current_controller = None
        self.db_path = db_path

        # モデルの遅延初期化用の参照を保持（必要になったら生成）
        self._models = {}

        # コントローラーのファクトリ辞書（キーは小文字で統一）
        self.controllers = {
            "home": lambda: self._create_home_controller(),
            "wordbook": lambda: self._create_wordbook_controller(),
            "wordlist": lambda: self._create_wordlist_controller(),
            "wordentry": lambda: self._create_wordentry_controller(),
            "qselect": lambda: self._create_qselect_controller(),
        }

        # 最初の画面を表示
        self.switch_view("home")

    # モデルファクトリ
    def _get_wordbook_model(self):
        if "wordbook" not in self._models:
            from Model.WordbookModel import WordbookModel
            self._models["wordbook"] = WordbookModel(db_path=self.db_path)
        return self._models["wordbook"]

    def _get_wordlist_model(self):
        if "wordlist" not in self._models:
            from Model.wordlist_model import WordListModel
            self._models["wordlist"] = WordListModel(db_path=self.db_path)
        return self._models["wordlist"]

    def _get_wordentry_model(self):
        if "wordentry" not in self._models:
            from Model.WordEntryModel import WordEntryModel
            self._models["wordentry"] = WordEntryModel(db_path=self.db_path)
        return self._models["wordentry"]

    def _get_qselect_model(self):
        if "qselect" not in self._models:
            from Model.Q_SelectModel import Q_SelectModel
            self._models["qselect"] = Q_SelectModel(db_path=self.db_path)
        return self._models["qselect"]

    # コントローラ生成ラッパ（各 factory は遅延インポート）
    def _create_home_controller(self):
        from Controller.HomeController import HomeController
        return HomeController(self)

    def _create_wordlist_controller(self):
        from Controller.wordlist_controller import WordListController
        return WordListController(self, self._get_wordlist_model())

    def _create_wordbook_controller(self):
        from Controller.WordbookController import WordbookController
        return WordbookController(self, self._get_wordbook_model())

    def _create_wordentry_controller(self):
        from Controller.WordEntryController import WordEntryController
        return WordEntryController(self, self._get_wordentry_model())

    def _create_qselect_controller(self):
        from Controller.Q_SelectController import Q_SelectController
        return Q_SelectController(self, self._get_qselect_model())
    
    def switch_view(self, view_name):
        """指定されたビューに切り替える"""
        if view_name not in self.controllers:
            print(f"Error: View '{view_name}' is not yet implemented.")
            return

        factory = self.controllers[view_name]
        if factory is None:
            print(f"Error: View '{view_name}' currently has no factory (not implemented).")
            return

        try:
            next_controller = factory()
        except Exception as e:
            print(f"Error: Failed to create controller for '{view_name}': {e}")
            return

        if self.current_controller:
            try:
                self.current_controller.hide()
            except Exception:
                pass

        self.current_controller = next_controller
        try:
            self.current_controller.show()
        except Exception as e:
            print(f"Error: Showing controller '{view_name}' failed: {e}")

        self.root.title(f"WordBook - {view_name.capitalize()}")

        if view_name == "wordbook":
            if hasattr(self.current_controller, "initialize_data_on_switch"):
                try:
                    self.current_controller.initialize_data_on_switch()
                except Exception as e:
                    print(f"Warning: initialize_data_on_switch failed: {e}")

    def open_wordbook(self, word_name: str):
        """wordbook 画面へ遷移し、遷移先コントローラに選択語を渡して表示させるヘルパ。"""
        # 切り替え
        self.switch_view("wordbook")
        # 生成されたコントローラに対して load_term を呼ぶ
        if self.current_controller and hasattr(self.current_controller, "load_term"):
            try:
                self.current_controller.load_term(word_name)
            except Exception as e:
                print(f"Warning: calling load_term failed: {e}")

    def start_quiz(self, term_list, mode: str = "random", num_questions: int = 10):
        """
        Q_SelectController から呼ばれるエントリポイント。
        term_list: 選択された単語ID あるいは単語名のリスト（Q_Select の実装に合わせる）
        mode: 'important' / 'random' 等
        num_questions: 出題数（任意）
        """
        # 遅延で QuizController を生成して開始する実装例
        try:
            # 生成（ファイル名は Q_Quiz_Controller.py / Q_Quiz_Model.py を想定）
            from Controller.Q_Quiz_Controller import Q_Quiz_Controller
            from Model.Q_Quiz_Model import Q_Quiz_Model
            # model に既存の単語モデルを渡す場合は _get_wordlist_model() 等を利用
            quiz_model = Q_Quiz_Model(db_model=self._get_wordlist_model(), use_stub=False)
            quiz_ctrl = Q_Quiz_Controller(self, quiz_model)
            # 切り替え
            if self.current_controller:
                try:
                    self.current_controller.hide()
                except Exception:
                    pass
            self.current_controller = quiz_ctrl
            quiz_ctrl.show()
            # Q_Quiz_Controller.start() のシグネチャに合わせて開始
            # Q_SelectController が渡す term_list の型に応じて、start の引数を調整してください
            quiz_ctrl.start(mode= "hide_word" if mode=="important" else "hide_word", tag=None, category=None, num_questions=num_questions)
        except Exception as e:
            print(f"Error: Failed to start quiz: {e}")