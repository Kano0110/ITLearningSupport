#wordEntryModel.py

from typing import Optional, List
from Model.BaseModel import BaseModel
import logging

logger = logging.getLogger(__name__)

class WordEntryModel(BaseModel):
    def __init__(self, db_path: Optional[str] = None, use_stub: bool = False):
        super().__init__(db_path=db_path)
        self.use_stub = use_stub
        self._stub_categories = ["生物", "物理", "数学", "歴史"]
        self._stub_tags = ["重要", "試験対策", "未学習", "復習"]

    def get_categories(self) -> List[str]:
        """既存のカテゴリ一覧を取得"""
        if self.use_stub:
            return self._stub_categories
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT category FROM terms WHERE category IS NOT NULL AND category != '' ORDER BY category;")
                rows = cur.fetchall()
                categorys = [row['category'] for row in rows if row['category']]
                return categorys
        except Exception:
            logger.exception("カテゴリ取得エラー")
            return self._stub_categories

    def get_all_tags(self) -> List[str]:
        """既存のタグ一覧を取得"""
        if self.use_stub:
            return self._stub_tags
        try:
            with self.get_conn() as conn:
                # 修正: 特定のタグの単語ではなく、タグ自体のリストを取得する
                cur = conn.execute("SELECT DISTINCT tag FROM terms WHERE tag IS NOT NULL AND tag != '' ORDER BY tag;")
                rows = cur.fetchall()
                tags = [row['tag'] for row in rows if row['tag']]
                return tags
        except Exception:
            logger.exception("タグ取得エラー")
            return self._stub_tags

    def create_word(self, word_name: str, explain: str, yomi: Optional[str]=None, category: Optional[str]=None, tag: Optional[str]=None) -> Optional[int]:
        """新規単語登録"""
        if not word_name or not explain:
            raise ValueError("単語名と解説は必須です。")
        if self.use_stub:
            return 1
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO terms (word_name, yomi, explain, category, tag) VALUES (?, ?, ?, ?, ?);",
                    (word_name, yomi, explain, category, tag)
                )
                conn.commit()
                return cur.lastrowid
        except Exception:
            logger.exception("単語作成エラー")
            return None