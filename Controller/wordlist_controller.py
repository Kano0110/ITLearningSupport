# Controller/wordlist_controller.py
import tkinter as tk
from typing import List, Optional, Callable
from Model.wordlist_model import WordListModel

class WordListController:
    """IT用語辞書のコントローラ
    
    用語の検索、フィルタリング、表示を管理します。
    """
    
    def __init__(self, root_controller, model: Optional[WordListModel] = None):
        """初期化
        
        Args:
            root_controller: AppControllerインスタンス
            model: WordListModelインスタンス（未指定時は新規作成）
        """
        self.app = root_controller
        self.model = model if model is not None else WordListModel()
        
        # フィルタ状態
        self.current_db_category: Optional[str] = None
        self.current_yomi_key: Optional[str] = None
        self.current_tag: Optional[str] = None
        self.current_search_query: str = ""
        self.use_yomi_filter: bool = True
        
        # ビュー管理
        self.view = None
        self.view_update_callback: Optional[Callable] = None
        self._last_terms: List[str] = []

    # --- 初期化・ビュー管理 ---
    def _ensure_view(self):
        """ビューが未生成の場合は生成し初期化"""
        if self.view is None:
            from View.wordlist_view import WordListView
            self.view = WordListView(self.app.root, self)
            try:
                self.initialize()
            except Exception as e:
                print(f"Warning: ensure_view initialize failed: {e}")

    def set_view_update_callback(self, callback: Callable):
        """ビューが更新コールバックを登録するメソッド
        
        Args:
            callback: (terms_list, message)を受け取る関数
        """
        self.view_update_callback = callback
        try:
            if self._last_terms:
                callback(self._last_terms, None)
            else:
                terms = self.model.get_all_terms()
                self._last_terms = terms
                callback(terms, None)
        except Exception as e:
            print(f"Warning: set_view_update_callback failed to push initial data: {e}")

    def _notify_view(self, terms: List[str], message: Optional[str] = None):
        """ビューに用語リストを通知
        
        Args:
            terms: 表示する用語リスト
            message: オプションのメッセージ
        """
        self._ensure_view()
        self._last_terms = terms
        
        if self.view_update_callback:
            self.view_update_callback(terms, message)
        elif hasattr(self.view, "update_list"):
            self.view.update_list(terms, message)
        
        self._update_filter_status_label()

    def _update_filter_status_label(self):
        """現在のフィルタ状態をステータスラベルに表示"""
        self._ensure_view()
        if not hasattr(self.view, "filter_status_label"):
            return
        
        status_parts = []
        if self.current_tag:
            status_parts.append(f"タグ: {self.current_tag}")
        if self.current_db_category:
            status_parts.append(f"カテゴリ: {self.current_db_category}")
        if self.current_yomi_key:
            status_parts.append(f"50音: {self.current_yomi_key}")
        if self.current_search_query:
            status_parts.append(f"検索: {self.current_search_query}")
        
        status_text = " | ".join(status_parts) if status_parts else "すべて表示"
        
        try:
            self.view.filter_status_label.config(text=status_text)
        except Exception as e:
            print(f"Warning: filter_status_label update failed: {e}")

    def initialize(self) -> bool:
        """初期化処理
        
        Returns:
            初期化成功の可否
        """
        if not self.model.is_db_available():
            self._notify_view([], "データベースが見つかりません")
            return False
        all_terms = self.model.get_all_terms()
        self._notify_view(all_terms)
        return True

    # --- フィルタリング ---
    def select_category(self, category: str):
        """カテゴリ選択（互換性のため残す）
        
        Args:
            category: カテゴリ名
        """
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

    # --- データ取得 ---
    def get_term_detail(self, word_name: str):
        """用語の詳細情報を取得"""
        return self.model.get_term_detail(word_name)

    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        return self.model.get_categories()

    def get_available_tags(self) -> List[str]:
        """利用可能なタグ一覧を取得"""
        return self.model.get_all_tags()
    
    def get_available_categorys(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得（別名）"""
        return self.model.get_all_categorys()

    def get_yomi_index(self) -> List[str]:
        """五十音インデックスを取得"""
        return self.model.get_yomi_keys()
    
    def get_stats(self):
        """統計情報を取得"""
        return self.model.get_stats()
    
    def select_tag(self, tag: str):
        """タグで絞り込み（他のフィルタをクリア）
        
        Args:
            tag: タグ名
        """
        self._clear_all_filters()
        self.current_tag = tag
        
        if not tag:
            self._notify_view([], f"タグ '{tag}' の用語はありません")
            return
        
        terms = self.model.get_terms_by_tag(tag)
        if not terms:
            self._notify_view([], f"タグ '{tag}' の用語はありません")
        else:
            self._notify_view(terms)

    def select_category_db(self, category: str):
        """DBカテゴリで絞り込み（他のフィルタをクリア）
        
        Args:
            category: カテゴリ名
        """
        self._clear_all_filters()
        self.current_db_category = category
        
        terms = self.model.get_terms_by_category(category)
        if not terms:
            self._notify_view([], f"カテゴリ '{category}' の用語はありません")
        else:
            self._notify_view(terms)

    def select_yomi(self, yomi_key: str):
        """50音で絞り込み（他のフィルタをクリア）
        
        Args:
            yomi_key: 50音のキー（あ、か、さ等）
        """
        self._clear_all_filters()
        self.current_yomi_key = yomi_key
        
        terms = self.model.get_terms_by_yomi(yomi_key)
        if not terms:
            self._notify_view([], f"{yomi_key}行の用語はありません")
        else:
            self._notify_view(terms)

    def _clear_all_filters(self):
        """全てのフィルタ状態をクリア"""
        self.current_db_category = None
        self.current_yomi_key = None
        self.current_tag = None
        self.current_search_query = ""

    def clear_tag(self):
        """タグフィルタをクリア"""
        self.current_tag = None
        self.apply_search(self.current_search_query)

    def clear_category(self):
        """全フィルタをクリアして全て表示"""
        self._clear_all_filters()
        all_terms = self.model.get_all_terms()
        self._notify_view(all_terms)

    def refresh_data(self):
        """データをリフレッシュして現在のフィルタを再適用"""
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
        """データベースが利用可能かチェック"""
        return self.model.is_db_available()

    def toggle_filter_mode(self):
        """フィルタモード（読み仮名/カテゴリ）を切り替え"""
        self.use_yomi_filter = not self.use_yomi_filter
        if hasattr(self, 'current_category') and self.current_category:
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

    # --- 画面遷移 ---
    def go_to_home(self):
        """Home画面へ遷移"""
        self.app.switch_view("home")

    def go_to_quiz(self):
        """問題選択画面へ遷移"""
        self.app.switch_view("qselect")

    def go_to_wordentry(self):
        """単語登録画面へ遷移"""
        self.app.switch_view("wordentry")

    def on_term_selected(self, word_name: str):
        """用語が選択されたときの処理
        
        Args:
            word_name: 選択された用語名
        """
        self.handle_go_wordbook(word_name)

    def handle_go_wordbook(self, word_name: Optional[str] = None):
        """単語帳画面へ遷移（現在のリストも渡す）
        
        Args:
            word_name: 表示する用語名（未指定時は先頭）
        """
        current_list = self._last_terms
        
        if word_name:
            self.app.switch_view("wordbook", word_name=word_name, context_list=current_list)
        else:
            self.app.switch_view("wordbook", context_list=current_list)