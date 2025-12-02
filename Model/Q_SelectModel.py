import logging
from typing import List, Optional

# BaseModelのインポート（環境に合わせて調整してください）
# from .BaseModel import BaseModel 
# ここではダミーとして仮定します。実際は元のimportを使用してください。
try:
    from .BaseModel import BaseModel
except ImportError:
    # テスト実行用ダミー
    class BaseModel:
        def __init__(self, db_path=None): self.db_path = db_path
        def get_conn(self): pass
        def is_db_available(self): return True

logger = logging.getLogger(__name__)

class Q_SelectModel(BaseModel):
    """問題選択画面のデータモデル"""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)

    def get_all_terms(self) -> List[str]:
        """全ての用語を取得"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT word_name FROM terms WHERE word_name IS NOT NULL ORDER BY word_name COLLATE NOCASE;")
                rows = cur.fetchall()
                return [row['word_name'] for row in rows]
        except Exception:
            logger.exception("全件取得エラー")
            return []

    def get_terms_by_filters(self, selected_tags: List[str], selected_categories: List[str]) -> List[str]:
        """
        選択されたタグとカテゴリに基づいて用語をフィルタリング
        AND条件ではなく、タグ条件 OR カテゴリ条件 のように
        「選択された条件のいずれかに合致するもの」とするか、
        「タグかつカテゴリ」とするかは要件によりますが、
        ここでは一般的な「(タグ IN (...)) AND (カテゴリ IN (...))」の実装にします。
        もし片方が空なら、そのフィルタは無視します。
        """
        if not selected_tags and not selected_categories:
            return self.get_all_terms()

        conditions = []
        params = []

        # タグフィルタ
        if selected_tags:
            placeholders = ','.join('?' * len(selected_tags))
            conditions.append(f"tag IN ({placeholders})")
            params.extend(selected_tags)

        # カテゴリフィルタ
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
        """利用可能なカテゴリをDBから取得"""
        try:
            with self.get_conn() as conn:
                # categoryカラムを参照
                cur = conn.execute("SELECT DISTINCT category FROM terms WHERE category IS NOT NULL ORDER BY category COLLATE NOCASE;")
                rows = cur.fetchall()
                return [row['category'] for row in rows if row['category']]
        except Exception:
            logger.exception("カテゴリ一覧取得エラー")
            return []

    def get_all_tags(self) -> List[str]:
        """データベースから全タグを取得"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT tag FROM terms WHERE tag IS NOT NULL ORDER BY tag COLLATE NOCASE;")
                rows = cur.fetchall()
                return [row['tag'] for row in rows if row['tag']]
        except Exception:
            logger.exception("タグ一覧取得エラー")
            return []

    def is_db_available(self) -> bool:
        return getattr(self, 'db_path', None) is not None