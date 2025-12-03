import logging
from typing import List, Optional

try:
    from .BaseModel import BaseModel
except ImportError:
    # テスト実行用ダミー
    class BaseModel:
        def __init__(self, db_path=None): 
            self.db_path = db_path
        def get_conn(self): 
            pass
        def is_db_available(self): 
            return True

logger = logging.getLogger(__name__)

class Q_SelectModel(BaseModel):
    """問題選択画面のデータモデル"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化
        
        Args:
            db_path: データベースファイルパス（未指定時はデフォルト）
        """
        super().__init__(db_path=db_path)

    def get_all_terms(self) -> List[str]:
        """全ての用語を取得
        
        Returns:
            全用語名のリスト（アルファベット順）
        """
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT word_name FROM terms "
                    "WHERE word_name IS NOT NULL "
                    "ORDER BY word_name COLLATE NOCASE;"
                )
                rows = cur.fetchall()
                return [row['word_name'] for row in rows]
        except Exception:
            logger.exception("全件取得エラー")
            return []

    def get_terms_by_filters(self, selected_tags: List[str], selected_categories: List[str]) -> List[str]:
        """選択されたタグとカテゴリに基づいて用語をフィルタリング
        
        タグとカテゴリの両方が選択されている場合はAND条件で絞り込む。
        片方のみ選択されている場合は、その条件のみで絞り込む。
        
        Args:
            selected_tags: 選択されたタグのリスト
            selected_categories: 選択されたカテゴリのリスト
            
        Returns:
            フィルタリングされた用語名のリスト
        """
        if not selected_tags and not selected_categories:
            return self.get_all_terms()

        conditions = []
        params = []

        if selected_tags:
            placeholders = ','.join('?' * len(selected_tags))
            conditions.append(f"tag IN ({placeholders})")
            params.extend(selected_tags)

        if selected_categories:
            placeholders = ','.join('?' * len(selected_categories))
            conditions.append(f"category IN ({placeholders})")
            params.extend(selected_categories)

        sql = "SELECT DISTINCT word_name FROM terms WHERE word_name IS NOT NULL"
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        sql += " ORDER BY word_name COLLATE NOCASE;"

        try:
            with self.get_conn() as conn:
                cur = conn.execute(sql, tuple(params))
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("フィルタリング取得エラー")
            return []

    def get_categories(self) -> List[str]:
        """利用可能なカテゴリをDBから取得
        
        Returns:
            カテゴリ名のリスト（アルファベット順）
        """
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT category FROM terms "
                    "WHERE category IS NOT NULL "
                    "ORDER BY category COLLATE NOCASE;"
                )
                rows = cur.fetchall()
                return [row['category'] for row in rows if row['category']]
        except Exception:
            logger.exception("カテゴリ一覧取得エラー")
            return []

    def get_all_tags(self) -> List[str]:
        """データベースから全タグを取得
        
        Returns:
            タグ名のリスト（アルファベット順）
        """
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT tag FROM terms "
                    "WHERE tag IS NOT NULL "
                    "ORDER BY tag COLLATE NOCASE;"
                )
                rows = cur.fetchall()
                return [row['tag'] for row in rows if row['tag']]
        except Exception:
            logger.exception("タグ一覧取得エラー")
            return []

    def is_db_available(self) -> bool:
        """データベースが利用可能かチェック
        
        Returns:
            データベースが利用可能な場合True
        """
        return getattr(self, 'db_path', None) is not None