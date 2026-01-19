#AppController.py
import traceback # デバッグ用

class AppController:
    """アプリケーション全体の画面遷移を統括するメインコントローラー"""

    def start(self):
        print("srtart called")

    def __init__(self, root, db_path=None):
        self.root = root
        self.root.geometry("600x520")
        self.current_controller = None
        self.db_path = db_path

        # 直前のビュー名を保持（Wordbook→Wordlistのときだけフィルタを維持する）
        self._last_view_name = None

        # コントローラーのキャッシュ（フィルタ状態などを保持するため再利用）
        self._controller_cache = {}

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
            "result": lambda: self._create_result_controller(),
            "auth": lambda: self._create_auth_controller(),  # 新規追加
            "sync": lambda: self._create_sync_controller()  # 新規追加

        }

        # 最初の画面を表示
        self.switch_view("home")

    # --- モデルファクトリ ---

    # 新規追加
    def _get_auth_model(self):
        if "auth" not in self._models:
            from Model.AuthModel import AuthModel
            self._models["auth"] = AuthModel(db_path=self.db_path)
        return self._models["auth"]
    
    def _get_sync_model(self):
        if "sync" not in self._models:
            from Model.SyncModel import SyncModel
            self._models["sync"] = SyncModel(db_path=self.db_path)
        return self._models["sync"]
    # 新規追加ここまで

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

    def _get_result_model(self):
        if "result" not in self._models:
            try:
                from Model.ResultModel import ResultModel
                self._models["result"] = ResultModel(db_path=self.db_path)
            except ImportError:
                print("Warning: ResultModel not found or import error.")
                self._models["result"] = None
        return self._models["result"]

    # --- コントローラ生成ラッパ ---

    # 新規追加
    def _create_auth_controller(self):
        from Controller.AuthController import AuthController
        return AuthController(self, self._get_auth_model())

    def _create_sync_controller(self):
        from Controller.SyncController import SyncController
        return SyncController(self, self._get_sync_model())
    # 新規追加ここまで

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

    def _create_result_controller(self):
        from Controller.ResultController import ResultController
        return ResultController(self, self._get_result_model())

     #<新規追加>
    def go_to_auth(self):
        """ログイン/登録画面へ遷移"""
        # AuthController経由で画面遷移
        self.switch_view("auth")

    def go_to_sync(self, username=None, password=None):
        """同期画面へ遷移し、ID/PASSがあれば自動接続を試みる"""
        print("DEBUG: go_to_sync が呼ばれました")
        
        # 画面切り替え実行
        self.switch_view("sync")
        
        # 切り替えが成功したかチェック（現在のコントローラがSyncControllerになっているか）
        # クラス名を文字列で確認することで、インポート不要でチェック
        current_class_name = self.current_controller.__class__.__name__
        
        if current_class_name != "SyncController":
            print(f"ERROR: SyncControllerへの切り替えに失敗しました。現在は {current_class_name} です。")
            print("Hint: SyncController.py のコードにエラーがないか、ターミナルの上の行のエラーログを確認してください。")
            return

        # 成功していれば情報を渡す
        if username and password:
            if hasattr(self.current_controller, "setup_with_credentials"):
                print(f"DEBUG: SyncControllerにクレデンシャルを渡します: {username}")
                self.current_controller.setup_with_credentials(username, password)
            else:
                print("DEBUG: SyncController に setup_with_credentials メソッドが見つかりません。スペルを確認してください。")
    # 新規追加ここまで

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

        is_new_instance = False
        try:
            if view_name in self._controller_cache:
                next_controller = self._controller_cache[view_name]
            else:
                next_controller = factory()
                self._controller_cache[view_name] = next_controller
                is_new_instance = True
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

        #新規追加
        next_controller.show()
        self.root.title(f"WordBook - {view_name.capitalize()}")
        #新規追加ここまで

        # Wordlistに戻るとき、直前がWordbook以外ならフィルタをリセット
        if view_name == "wordlist" and self._last_view_name != "wordbook":
            if hasattr(self.current_controller, "reset_filters_to_all"):
                try:
                    self.current_controller.reset_filters_to_all()
                except Exception as e:
                    print(f"Warning: reset_filters_to_all failed: {e}")

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
            if is_new_instance and hasattr(self.current_controller, "initialize"):
                self.current_controller.initialize()
            elif hasattr(self.current_controller, "refresh_data"):
                self.current_controller.refresh_data()

        # 現在のビュー名を保存（次回判定用）
        self._last_view_name = view_name

    def open_wordbook(self, word_name: str):
        """wordbook 画面へ遷移し、遷移先コントローラに選択語を渡して表示させるヘルパ。"""
        # switch_view に引数を渡すように統一
        self.switch_view("wordbook", word_name=word_name)

    def start_quiz(self, term_list, mode: str = "hide_word", num_questions: int = 10,selected_tags=None,
    selected_categories=None):
        try:
            from Controller.Q_quiz_Controller import Q_Quiz_Controller
            quiz_model = self._get_quiz_model()
            if not quiz_model:
                print("Error: Quiz model could not be initialized.")
                return

            quiz_ctrl = Q_Quiz_Controller(self, quiz_model)

            self._controller_cache["quiz"] = quiz_ctrl

            if self.current_controller:
                try:
                    self.current_controller.hide()
                except Exception:
                    pass

            self.current_controller = quiz_ctrl
            quiz_ctrl.show()

            # 修正：Q_SelectController から渡された mode を使う
            if hasattr(quiz_ctrl, "start"):
                quiz_ctrl.start(selected_terms=term_list, mode=mode, num_questions=num_questions,selected_tags=selected_tags,selected_categories=selected_categories)
            elif hasattr(quiz_ctrl, "start_quiz"):
                quiz_ctrl.start_quiz(term_list)

        except Exception as e:
            print(f"Error: Failed to start quiz: {e}")
            traceback.print_exc()

    def show_quiz_result(self, correct_count, total_questions, category=None, tag=None, wronged_terms=None,selected_terms=None, mode=None, num_questions=None,elapsed_time=None):
        """結果画面へ遷移"""
        self.switch_view("result")
        if hasattr(self.current_controller, "set_result"):
            self.current_controller.set_result(
                correct_count=correct_count,
                total_questions=total_questions,
                category=category,
                tag=tag,
                wronged_terms=wronged_terms,
                selected_terms=selected_terms,
                mode=mode,
                num_questions=num_questions,
                elapsed_time=elapsed_time
            )
