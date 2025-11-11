# Controller/AppController.py

class AppController:
    """アプリケーション全体の画面遷移を統括するメインコントローラー"""
    def __init__(self, root, db_path=None):
        self.root = root
        self.root.geometry("600x400")
        self.current_controller = None
        self.db_path = db_path

        # モデルの遅延初期化用の参照を保持（必要になったら生成）
        self._models = {}

        # コントローラーのファクトリ辞書
        self.controllers = {
            "home": lambda: self._create_home_controller(),
            "wordbook": lambda: self._create_wordbook_controller(),
            "wordlist": lambda: self._create_wordlist_controller(),
            "wordentry": None,
            "quiz": None,
        }

        # 最初の画面を表示
        self.switch_view("home")

    # モデルファクトリ例
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

    # コントローラ生成ラッパ
    def _create_home_controller(self):
        from Controller.HomeController import HomeController
        return HomeController(self)

    def _create_wordbook_controller(self):
        from Controller.WordbookController import WordbookController
        return WordbookController(self, self._get_wordbook_model())

    def _create_wordlist_controller(self):
        from Controller.wordlist_controller import WordListController
        return WordListController(self, self._get_wordlist_model())

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