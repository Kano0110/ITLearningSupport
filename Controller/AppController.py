import traceback # デバッグ用

class AppController:
    """アプリケーション全体の画面遷移を統括するメインコントローラー"""
    def __init__(self, root, db_path=None):
        self.root = root
        self.root.geometry("600x500")
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
            "quiz": lambda: self._create_quiz_controller(),
            
        }

        # 最初の画面を表示
        self.switch_view("home")

    # --- モデルファクトリ ---
    def _get_wordbook_model(self):
        if "wordbook" not in self._models:
            from Model.WordbookModel import WordBookModel
            self._models["wordbook"] = WordBookModel(db_path=self.db_path)
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

    def _get_quiz_model(self):
        if "quiz" not in self._models:
            try:
                from Model.Q_quiz_Model import Q_Quiz_Model
                self._models["quiz"] = Q_Quiz_Model(db_path=self.db_path)
            except ImportError:
                print("Warning: Q_Quiz_Model not found or import error.")
                self._models["quiz"] = None
        return self._models["quiz"]

    # --- コントローラ生成ラッパ ---
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

    def _create_quiz_controller(self):
        from Controller.Q_quiz_Controller import Q_Quiz_Controller
        return Q_Quiz_Controller(self, self._get_quiz_model())

    # --- 画面遷移 (修正: 引数を追加) ---
    def switch_view(self, view_name, word_name: str = None, context_list: list = None):
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
            traceback.print_exc()
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

        # Wordbookへの遷移時の処理 (修正: 引数を渡す)
        if view_name == "wordbook":
            if hasattr(self.current_controller, "initialize_data_on_switch"):
                try:
                    # 最新のWordbookControllerは context_list も受け取る
                    self.current_controller.initialize_data_on_switch(word_name, context_list)
                except TypeError:
                    # 引数を受け取らない古いバージョンの場合、または引数が合わない場合のフォールバック
                    try:
            
                        self.current_controller.initialize_data_on_switch(word_name)
                    except TypeError:
                        self.current_controller.initialize_data_on_switch()
                except Exception as e:
                    print(f"Warning: initialize_data_on_switch failed: {e}")

        # Wordlistへの遷移時の処理
        if view_name == "wordlist":
            if hasattr(self.current_controller, "initialize"):
                self.current_controller.initialize()

    def open_wordbook(self, word_name: str):
        """wordbook 画面へ遷移し、遷移先コントローラに選択語を渡して表示させるヘルパ。"""
        # switch_view に引数を渡すように統一
        self.switch_view("wordbook", word_name=word_name)

    def start_quiz(self, term_list, mode: str = "random", num_questions: int = 10):
        """
        Q_SelectController から呼ばれるエントリポイント。
        """
        try:
            # 生成
            from Controller.Q_quiz_Controller import Q_Quiz_Controller
            
            quiz_model = self._get_quiz_model()
            if not quiz_model:
                 print("Error: Quiz model could not be initialized.")
                 return

            quiz_ctrl = Q_Quiz_Controller(self, quiz_model)
            
            # 切り替え
            if self.current_controller:
                try:
                    self.current_controller.hide()
                except Exception:
                    pass
            
            self.current_controller = quiz_ctrl
            quiz_ctrl.show()
            
            # クイズ開始メソッドを呼ぶ (Controllerの実装に合わせて調整)
            if hasattr(quiz_ctrl, "start"):
                quiz_ctrl.start(mode="hide_word", tag=None, category=None, num_questions=num_questions)
            elif hasattr(quiz_ctrl, "start_quiz"):
                quiz_ctrl.start_quiz(term_list)
                
        except Exception as e:
            print(f"Error: Failed to start quiz: {e}")
            traceback.print_exc()
    
    def show_quiz_result(self, correct_count, total_questions):
        from View.Q_resultView import Q_ResultView
        result_view = Q_ResultView(self.root, controller=self,
                                correct_count=correct_count,
                                total_questions=total_questions)
        self._switch_view(result_view)
