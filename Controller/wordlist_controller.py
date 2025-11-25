# Controller/wordlist_controller.py
import tkinter as tk
from typing import List, Optional, Callable
from Model.wordlist_model import WordListModel

class WordListController:
    """IT用語辞書のコントローラ"""
    
    def __init__(self, root_controller, model: Optional[WordListModel] = None):
        self.app = root_controller
        self.model = model if model is not None else WordListModel()
        self.current_db_category: Optional[str] = None
        self.current_yomi_key: Optional[str] = None
        self.current_tag: Optional[str] = None
        self.current_search_query: str = ""
        self.use_yomi_filter: bool = True
        self.view_update_callback: Optional[Callable] = None
        self.view = None
        self._last_terms = [] # 現在表示中のリストを保持する変数

    def _ensure_view(self):
        if self.view is None:
            from View.wordlist_view import WordListView
            self.view = WordListView(self.app.root, self)
            try:
                self.initialize()
            except Exception as e:
                print(f"Warning: ensure_view initialize failed: {e}")

    def set_view_update_callback(self, callback: Callable):
        self.view_update_callback = callback
        try:
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
        # 表示中のリストをキャッシュ（これを次へ/前へ機能で使う）
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

    # --- フィルタリング関連 ---
    def select_category(self, category: str):
        self.current_category = category
        self.current_search_query = ""
        if self.use_yomi_filter:
            terms = self.model.get_terms_by_yomi(category)
        else:
            terms = self.model.get_terms_by_category(category)
        if not terms:
            self._notify_view([], f"{category}行の用語はありません")
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
            return

        if getattr(self, 'current_db_category', None):
            self.select_category_db(self.current_db_category)
            return
        if getattr(self, 'current_yomi_key', None):
            self.select_yomi(self.current_yomi_key)
            return
        if getattr(self, 'current_tag', None):
            self.select_tag(self.current_tag)
            return
        if getattr(self, 'current_category', None):
            self.select_category(self.current_category)
            return

        all_terms = self.model.get_all_terms()
        self._notify_view(all_terms)

    def clear_search(self):
        self.apply_search("")

    def get_term_detail(self, word_name: str):
        return self.model.get_term_detail(word_name)

    def get_available_categories(self):
        return self.model.get_categories()

    def get_available_tags(self):
        return self.model.get_all_tags()
    
    def select_tag(self, tag: str):
        self.current_tag = tag
        self.current_search_query = ""
        if not tag:
            self._notify_view([], f"タグ '{tag}' の用語はありません")
            return
        terms = self.model.get_terms_by_tag(tag)
        if not terms:
            self._notify_view([], f"タグ '{tag}' の用語はありません")
        else:
            self._notify_view(terms)

    def clear_tag(self):
        self.current_tag = None
        self.apply_search(self.current_search_query)

    def get_available_categorys(self):
        return self.model.get_all_categorys()

    def get_yomi_index(self):
        return self.model.get_yomi_keys()

    def select_category_db(self, category: str):
        self.current_db_category = category
        self.current_yomi_key = None
        self.current_search_query = ""
        terms = self.model.get_terms_by_category(category)
        if not terms:
            self._notify_view([], f"カテゴリ '{category}' の用語はありません")
        else:
            self._notify_view(terms)

    def select_yomi(self, yomi_key: str):
        self.current_yomi_key = yomi_key
        self.current_db_category = None
        self.current_search_query = ""
        terms = self.model.get_terms_by_yomi(yomi_key)
        if not terms:
            self._notify_view([], f"{yomi_key}行の用語はありません")
        else:
            self._notify_view(terms)

    def clear_category(self):
        self.current_db_category = None
        self.current_yomi_key = None
        if self.current_tag:
            self.select_tag(self.current_tag)
        else:
            self.apply_search(self.current_search_query)

    def get_stats(self):
        return self.model.get_stats()

    def refresh_data(self):
        self.model.get_all_terms(force_refresh=True)
        if self.current_search_query:
            self.apply_search(self.current_search_query)
        elif self.current_db_category:
            self.select_category_db(self.current_db_category)
        elif self.current_yomi_key:
            self.select_yomi(self.current_yomi_key)
        elif self.current_tag:
            self.select_tag(self.current_tag)
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
        try:
            self._ensure_view()
        except Exception as e:
            print(f"Warning: show failed to ensure view: {e}")
        
        try:
            self.refresh_data()
        except Exception as e:
            print(f"Warning: refresh_data failed: {e}")
        
        if hasattr(self.view, "show"):
            try:
                self.view.show()
            except Exception as e:
                print(f"Warning: view.show() failed: {e}")
        else:
            try:
                all_terms = self.model.get_all_terms()
                self._notify_view(all_terms)
            except Exception as e:
                print(f"Warning: fallback notify failed: {e}")

    def hide(self):
        if hasattr(self.view, "hide"):
            self.view.hide()

    def go_to_home(self):
        self.app.switch_view("home")

    def go_to_wordentry(self):
        self.app.switch_view("wordentry")

    def on_term_selected(self, word_name: str):
        """用語が選択されたときの処理 -> 詳細画面へ"""
        self.handle_go_wordbook(word_name)

    def handle_go_wordbook(self, word_name: str = None):
        """単語帳画面へ遷移する（現在の一覧リストも渡す）"""
        # 現在のリスト（フィルタ済み）を取得
        current_list = getattr(self, "_last_terms", [])
        
        if word_name:
            # context_listとして現在のリストを渡す
            self.app.switch_view("wordbook", word_name=word_name, context_list=current_list)
        else:
            self.app.switch_view("wordbook", context_list=current_list)