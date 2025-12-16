# Controller/wordlist_controller.py
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
        self.current_other: bool = False
        
        # ビュー管理
        self.view = None
        self.view_update_callback: Optional[Callable] = None
        self._last_terms: List[str] = []
        self._apply_after_id: Optional[str] = None  # フィルタ適用のデバウンスID

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
        if self.current_other:
            status_parts.append("その他")
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
    def apply_search(self, query: str):
        self.current_search_query = query.strip()
        self._schedule_apply_filters()

    def clear_search(self):
        self.apply_search("")

    # --- フィルタ適用ヘルパ ---
    def _apply_filters(self):
        """現在のフィルタ（タグ・カテゴリ・50音・検索・その他）をまとめて適用"""
        base_terms = self.model.get_all_terms()
        terms = set(base_terms)

        has_filter = False

        if self.current_db_category:
            has_filter = True
            terms &= set(self.model.get_terms_by_category(self.current_db_category))

        if self.current_yomi_key:
            has_filter = True
            terms &= set(self.model.get_terms_by_yomi(self.current_yomi_key))

        if self.current_tag:
            has_filter = True
            terms &= set(self.model.get_terms_by_tag(self.current_tag))

        if self.current_other:
            has_filter = True
            terms = {t for t in terms if t and not self._is_japanese_char(t[0])}

        if self.current_search_query:
            has_filter = True
            searched = set(self.model.search_terms(self.current_search_query))
            terms &= searched

        if not has_filter:
            self._notify_view(base_terms)
            return

        result = sorted(list(terms))
        if not result:
            self._notify_view([], "該当する用語はありません")
        else:
            self._notify_view(result)

    def _schedule_apply_filters(self, delay_ms: int = 80):
        """フィルタ適用をデバウンスしてスケジュール"""
        if self._apply_after_id is not None and hasattr(self.app, 'root'):
            try:
                self.app.root.after_cancel(self._apply_after_id)
            except Exception:
                pass
            self._apply_after_id = None
        def _do_apply():
            self._apply_after_id = None
            try:
                self._apply_filters()
            except Exception as e:
                print(f"Warning: _apply_filters failed: {e}")
        if hasattr(self.app, 'root'):
            self._apply_after_id = self.app.root.after(delay_ms, _do_apply)
        else:
            _do_apply()

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
        return self.model.get_all_categories()

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
        self.current_tag = tag
        self.current_other = False
        if not tag:
            self._notify_view([], f"タグ '{tag}' の用語はありません")
            return
        self._schedule_apply_filters()

    def select_category_db(self, category: str):
        """DBカテゴリで絞り込み（他のフィルタをクリア）
        
        Args:
            category: カテゴリ名
        """
        self.current_db_category = category
        self.current_other = False
        self._schedule_apply_filters()

    def select_yomi(self, yomi_key: str):
        """50音で絞り込み（他のフィルタをクリア）
        
        Args:
            yomi_key: 50音のキー（あ、か、さ等）
        """
        self._clear_all_filters()
        self.current_yomi_key = yomi_key
        self._schedule_apply_filters()

    def select_other(self):
        """その他（日本語以外）で絞り込み（他のフィルタをクリア）"""
        self._clear_all_filters()
        self.current_other = True
        self._schedule_apply_filters()

    def _is_japanese_char(self, char: str) -> bool:
        """文字が日本語かどうかを判定
        
        Args:
            char: 判定対象の文字
            
        Returns:
            日本語文字の場合True
        """
        # Unicode範囲で日本語文字を判定
        code = ord(char)
        # ひらがな: U+3040-U+309F
        if 0x3040 <= code <= 0x309F:
            return True
        # カタカナ: U+30A0-U+30FF
        if 0x30A0 <= code <= 0x30FF:
            return True
        # 漢字: U+4E00-U+9FFF
        if 0x4E00 <= code <= 0x9FFF:
            return True
        # その他の日本語記号: U+3000-U+303F（最後のーなど）
        if 0x3000 <= code <= 0x303F:
            return True
        return False

    def _clear_all_filters(self):
        """全てのフィルタ状態をクリア"""
        self.current_db_category = None
        self.current_yomi_key = None
        self.current_tag = None
        self.current_search_query = ""
        self.current_other = False

    def reset_filters_to_all(self):
        """フィルタを初期化し、全件表示に戻す（入力UIもクリア）"""
        self._clear_all_filters()
        all_terms = self.model.get_all_terms()
        # 入力UIリセット
        if self.view is not None:
            if hasattr(self.view, 'tag_var'):
                try:
                    self.view.tag_var.set("")
                except Exception:
                    pass
            if hasattr(self.view, 'category_var'):
                try:
                    self.view.category_var.set("")
                except Exception:
                    pass
            if hasattr(self.view, 'search_var'):
                try:
                    self.view.search_var.set("")
                except Exception:
                    pass
        self._notify_view(all_terms)

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
        self._schedule_apply_filters()

    def is_ready(self) -> bool:
        """データベースが利用可能かチェック"""
        return self.model.is_db_available()

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
        # 画面非表示時に保留しているフィルタ適用をキャンセル
        if self._apply_after_id is not None and hasattr(self.app, 'root'):
            try:
                self.app.root.after_cancel(self._apply_after_id)
            except Exception:
                pass
            self._apply_after_id = None
            

    # --- 画面遷移 ---
    def go_to_home(self):
        """Home画面へ遷移"""
        if self._apply_after_id is not None and hasattr(self.app, 'root'):
            try:
                self.app.root.after_cancel(self._apply_after_id)
            except Exception:
                pass
            self._apply_after_id = None
        self.app.switch_view("home")

    def go_to_quiz(self):
        """問題選択画面へ遷移"""
        if self._apply_after_id is not None and hasattr(self.app, 'root'):
            try:
                self.app.root.after_cancel(self._apply_after_id)
            except Exception:
                pass
            self._apply_after_id = None
        self.app.switch_view("qselect")

    def go_to_wordentry(self):
        """単語登録画面へ遷移"""
        if self._apply_after_id is not None and hasattr(self.app, 'root'):
            try:
                self.app.root.after_cancel(self._apply_after_id)
            except Exception:
                pass
            self._apply_after_id = None
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