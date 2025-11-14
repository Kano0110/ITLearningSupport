# Controller/wordlist_controller.py
from typing import List, Optional, Callable
from Model.wordlist_model import WordListModel

class WordListController:
    def __init__(self, root_controller, model: Optional[WordListModel] = None):
        self.app = root_controller
        self.model = model if model is not None else WordListModel()
        self.current_category: Optional[str] = None
        self.current_tag: Optional[str] = None
        self.current_search_query: str = ""
        self.use_yomi_filter: bool = True
        self.view_update_callback: Optional[Callable] = None
        self.view = None  # 遅延生成

    def _ensure_view(self):
        if self.view is None:
            from View.wordlist_view import WordListView
            self.view = WordListView(self.app.root, self)
            # ビューが作られたら直ちに初期データを通知して描画させる
            try:
                # initialize() は DB 存在チェックと最初の描画呼び出しを行う
                self.initialize()
            except Exception as e:
                print(f"Warning: ensure_view initialize failed: {e}")

    def set_view_update_callback(self, callback: Callable):
        """View がコールバックを登録したときに直ちに現在データを渡す"""
        self.view_update_callback = callback
        try:
            # 可能ならキャッシュ済みデータを渡す（無ければ model から取得）
            if getattr(self, "_last_terms", None) is not None:
                callback(self._last_terms, None)
            else:
                terms = self.model.get_all_terms()
                self._last_terms = terms
                callback(terms, None)
        except Exception as e:
            print(f"Warning: set_view_update_callback failed to push initial data: {e}")

    def _notify_view(self, terms: List[str], message: Optional[str] = None):
        self._ensure_view()
        # キャッシュ
        self._last_terms = terms
        if self.view_update_callback:
            self.view_update_callback(terms, message)
        else:
            if hasattr(self.view, "update_list"):
                self.view.update_list(terms, message)

    def initialize(self):
        if not self.model.is_db_available():
            self._notify_view([], "データベースが見つかりません")
            return False
        all_terms = self.model.get_all_terms()
        self._notify_view(all_terms)
        return True

    def select_category(self, category: str):
        self.current_category = category
        self.current_search_query = ""
        if self.use_yomi_filter:
            terms = self.model.get_terms_by_yomi(category)
        else:
            terms = self.model.get_terms_by_category(category)
        if not terms:
            message = f"{category}行の用語はありません"
            self._notify_view([], message)
        else:
            self._notify_view(terms)

    def clear_category(self):
        self.current_category = None
        self.apply_search(self.current_search_query)

    def apply_search(self, query: str):
        self.current_search_query = query.strip()
        if self.current_search_query:
            terms = self.model.search_terms(self.current_search_query)
            if not terms:
                self._notify_view([], "該当する用語はありません")
            else:
                self._notify_view(terms)
        else:
            if self.current_category:
                self.select_category(self.current_category)
            else:
                all_terms = self.model.get_all_terms()
                self._notify_view(all_terms)

    def clear_search(self):
        self.apply_search("")

    def get_term_detail(self, word_name: str):
        return self.model.get_term_detail(word_name)

    def get_available_categories(self):
        return self.model.get_categories()

    def get_available_tags(self):
        """利用可能なタグ一覧を取得"""
        return self.model.get_all_tags()

    def select_tag(self, tag: str):
        """タグを選択して用語をフィルタリング"""
        self.current_tag = tag
        self.current_category = None
        self.current_search_query = ""
        terms = self.model.get_terms_by_tag(tag)
        if not terms:
            message = f"タグ '{tag}' の用語はありません"
            self._notify_view([], message)
        else:
            self._notify_view(terms)

    def clear_tag(self):
        """タグフィルタをクリア"""
        self.current_tag = None
        self.apply_search(self.current_search_query)

    def get_stats(self):
        return self.model.get_stats()

    def refresh_data(self):
        self.model.get_all_terms(force_refresh=True)
        if self.current_search_query:
            self.apply_search(self.current_search_query)
        elif self.current_category:
            self.select_category(self.current_category)
        else:
            all_terms = self.model.get_all_terms()
            self._notify_view(all_terms)

    def is_ready(self) -> bool:
        return self.model.is_db_available()

    def toggle_filter_mode(self):
        self.use_yomi_filter = not self.use_yomi_filter
        if self.current_category:
            self.select_category(self.current_category)

    def show(self):
    # view が未生成なら生成して初期描画させる
        try:
            self._ensure_view()
        except Exception as e:
            print(f"Warning: show failed to ensure view: {e}")
        # view が生成されていれば必ず表示処理を呼ぶ
        if hasattr(self.view, "show"):
            try:
                self.view.show()
            except Exception as e:
                print(f"Warning: view.show() failed: {e}")
        else:
            # デバッグ用フォールバック: view が None のままなら初期データを直接通知しておく
            try:
                all_terms = self.model.get_all_terms()
                self._notify_view(all_terms)
            except Exception as e:
                print(f"Warning: fallback notify failed: {e}")

    def hide(self):
        if hasattr(self.view, "hide"):
            self.view.hide()

    def go_to_home(self):
        """Home画面への遷移"""
        try:
            self.app.switch_view("home")
        except Exception as e:
            print(f"Error: Failed to switch to home: {e}")

    def go_to_wordentry(self):
        """WordEntry画面への遷移"""
        try:
            self.app.switch_view("wordentry")
        except Exception as e:
            print(f"Error: Failed to switch to wordentry: {e}")

    def on_term_selected(self, word_name: str):
        """用語が選択されたときの処理。
        AppController に wordbook 画面を開くよう依頼する。
        """
        # 1) 取得可能なら詳細を取得してキャッシュ（任意）
        detail = self.get_term_detail(word_name)

        # 2) AppController に遷移依頼（選択語を渡す）
        if hasattr(self.app, "open_wordbook"):
            # AppController 側のヘルパに委譲（推奨）
            try:
                self.app.open_wordbook(word_name)
                return
            except Exception:
                pass

        # 3) 既存の switch_view を使う簡易フォールバック: open → load_term を呼ぶ
        try:
            self.app.switch_view("wordbook")
            # 次の controller が生成された直後に load_term を呼べるようにする
            if hasattr(self.app.current_controller, "load_term"):
                self.app.current_controller.load_term(word_name)
        except Exception as e:
            print(f"Error: Failed to open wordbook for '{word_name}': {e}")
            # フォールバックでローカル表示
            if detail:
                if hasattr(self, "_ensure_view"):
                    # もし view があるならローカルで表示
                    try:
                        self._ensure_view()
                        if hasattr(self.view, "_show_detail_window"):
                            self.view._show_detail_window(detail)
                            return
                    except Exception:
                        pass
                # 最終手段で messagebox
                from tkinter import messagebox
                messagebox.showwarning("警告", f"'{word_name}'の詳細情報を表示できませんでした")