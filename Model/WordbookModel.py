"""
Model層: 単語の詳細取得、更新、削除
"""
from typing import Optional, Dict
from Model.BaseModel import BaseModel
import logging

logger = logging.getLogger(__name__)

class WordBookModel(BaseModel):
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)

    def get_by_id(self, word_id: int) -> Optional[Dict]:
        """IDに基づいて詳細を取得"""
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT id, word_name AS name, explain AS desc, tag, category, yomi FROM terms WHERE id = ? LIMIT 1;",
                    (word_id,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("ID検索エラー")
            return None

    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        """単語名に基づいて詳細を取得"""
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT id, word_name AS name, explain AS desc, tag, category, yomi FROM terms WHERE word_name = ? LIMIT 1;",
                    (word_name,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("詳細取得エラー")
            return None

    # 追加: デフォルト表示用に最初の単語名を取得するメソッド
    def get_first_word_name(self) -> Optional[str]:
        """データベースの最初の単語名を取得"""
        try:
            with self._get_connection() as conn:
                cur = conn.execute("SELECT word_name FROM terms ORDER BY id ASC LIMIT 1;")
                row = cur.fetchone()
                return row["word_name"] if row else None
        except Exception:
            logger.exception("最初の単語取得エラー")
            return None

    def update_term(self, word_id: int, word_name: str = None, explain: str = None,
                    tag: str = None, category: str = None, yomi: str = None) -> bool:
        """用語の更新"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE terms 
                    SET word_name = COALESCE(?, word_name), 
                        explain = COALESCE(?, explain), 
                        tag = COALESCE(?, tag), 
                        category = COALESCE(?, category),
                        yomi = COALESCE(?, yomi)
                    WHERE id = ?;
                    """,
                    (word_name, explain, tag, category, yomi, word_id)
                )
                conn.commit()
            return True
        except Exception:
            logger.exception("更新エラー")
            return False

    def delete_term(self, word_id: int) -> bool:
        """用語の削除"""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM terms WHERE id = ?;", (word_id,))
                conn.commit()
            return True
        except Exception:
            logger.exception("削除エラー")
            return False