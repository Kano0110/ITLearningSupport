"""
Controller層: ModelとViewの橋渡し、ビジネスロジックの制御
"""
from typing import List, Optional, Callable
from Model.wordlist_model import WordListModel


class WordListController:
    """IT用語辞書のコントローラ"""
    
    def __init__(self):
        self.model = WordListModel()
        self.current_category: Optional[str] = None
        self.current_search_query: str = ""
        self.use_yomi_filter: bool = True  # 読み仮名でフィルタするかどうか
        self.view_update_callback: Optional[Callable] = None
    
    def set_view_update_callback(self, callback: Callable):
        """
        Viewの更新用コールバックを設定
        
        Args:
            callback: View更新時に呼び出される関数
        """
        self.view_update_callback = callback
    
    def _notify_view(self, terms: List[str], message: Optional[str] = None):
        """
        Viewに更新を通知
        
        Args:
            terms: 表示する用語のリスト
            message: 空の場合に表示するメッセージ
        """
        if self.view_update_callback:
            self.view_update_callback(terms, message)
    
    def initialize(self):
        """
        初期化処理（アプリ起動時）
        """
        if not self.model.is_db_available():
            self._notify_view([], "データベースが見つかりません")
            return False
        
        # 全件を取得してキャッシュ
        all_terms = self.model.get_all_terms()
        self._notify_view(all_terms)
        return True
    
    def select_category(self, category: str):
        """
        カテゴリ（五十音行）を選択
        
        Args:
            category: カテゴリ名（'あ', 'か', 'さ'など）
        """
        self.current_category = category
        self.current_search_query = ""  # 検索をクリア
        
        # 読み仮名（yomi）でフィルタするか、categoryカラムでフィルタするか
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
        """
        カテゴリ選択を解除（全件表示に戻る）
        """
        self.current_category = None
        self.apply_search(self.current_search_query)
    
    def apply_search(self, query: str):
        """
        検索を適用
        
        Args:
            query: 検索クエリ
        """
        self.current_search_query = query.strip()
        
        if self.current_search_query:
            # 検索がある場合は全件から検索（カテゴリ選択は無視）
            terms = self.model.search_terms(self.current_search_query)
            if not terms:
                self._notify_view([], "該当する用語はありません")
            else:
                self._notify_view(terms)
        else:
            # 検索が空の場合
            if self.current_category:
                # カテゴリが選択されていればそのカテゴリを表示
                self.select_category(self.current_category)
            else:
                # カテゴリ未選択なら全件表示
                all_terms = self.model.get_all_terms()
                self._notify_view(all_terms)
    
    def clear_search(self):
        """
        検索をクリア
        """
        self.apply_search("")
    
    def get_term_detail(self, word_name: str) -> Optional[dict]:
        """
        用語の詳細情報を取得
        
        Args:
            word_name: 用語名
            
        Returns:
            用語の詳細情報、見つからない場合はNone
        """
        return self.model.get_term_detail(word_name)
    
    def get_available_categories(self) -> List[str]:
        """
        利用可能なカテゴリのリストを取得
        
        Returns:
            カテゴリのリスト
        """
        return self.model.get_categories()
    
    def get_stats(self) -> dict:
        """
        統計情報を取得
        
        Returns:
            統計情報の辞書
        """
        return self.model.get_stats()
    
    def refresh_data(self):
        """
        データを再読み込み（キャッシュをクリア）
        """
        self.model.get_all_terms(force_refresh=True)
        
        # 現在の状態に応じて再表示
        if self.current_search_query:
            self.apply_search(self.current_search_query)
        elif self.current_category:
            self.select_category(self.current_category)
        else:
            all_terms = self.model.get_all_terms()
            self._notify_view(all_terms)
    
    def is_ready(self) -> bool:
        """
        コントローラが使用可能な状態かチェック
        
        Returns:
            使用可能ならTrue
        """
        return self.model.is_db_available()
    
    def add_term(self, word_name: str, yomi: str = None, explain: str = None,
                 tag: str = None, category: str = None) -> bool:
        """
        新しい用語を追加
        
        Args:
            word_name: 単語名
            yomi: 読み仮名
            explain: 説明
            tag: タグ
            category: カテゴリ
            
        Returns:
            成功した場合True
        """
        success = self.model.add_term(word_name, yomi, explain, tag, category)
        if success:
            self.refresh_data()
        return success
    
    def update_term(self, word_name: str, yomi: str = None, explain: str = None,
                   tag: str = None, category: str = None) -> bool:
        """
        用語を更新
        
        Args:
            word_name: 単語名
            yomi: 読み仮名
            explain: 説明
            tag: タグ
            category: カテゴリ
            
        Returns:
            成功した場合True
        """
        success = self.model.update_term(word_name, yomi, explain, tag, category)
        if success:
            self.refresh_data()
        return success
    
    def delete_term(self, word_name: str) -> bool:
        """
        用語を削除
        
        Args:
            word_name: 単語名
            
        Returns:
            成功した場合True
        """
        success = self.model.delete_term(word_name)
        if success:
            self.refresh_data()
        return success
    
    def toggle_filter_mode(self):
        """
        フィルタモード（yomi/category）を切り替え
        """
        self.use_yomi_filter = not self.use_yomi_filter
        
        # 現在カテゴリが選択されていれば再適用
        if self.current_category:
            self.select_category(self.current_category)
