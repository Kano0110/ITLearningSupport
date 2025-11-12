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
        self._stub_makers = ["松下","日立","東芝","ソニー","シャープ","三井","三菱","住友","安田"]

    def get_categories(self) -> List[str]:
        if self.use_stub:
            return self._stub_categories
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT category FROM terms WHERE category IS NOT NULL ORDER BY category;")
                return [r["category"] for r in cur.fetchall()]
        except Exception:
            logger.exception("カテゴリ取得エラー")
            return self._stub_categories

    def get_makers(self) -> List[str]:
        if self.use_stub:
            return self._stub_makers
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT maker FROM terms WHERE maker IS NOT NULL ORDER BY maker;")
                rows = [r["maker"] for r in cur.fetchall()]
                return rows if rows else self._stub_makers
        except Exception:
            logger.exception("メーカー取得エラー")
            return self._stub_makers

    def create_word(self, word_name: str, explain: str, category: Optional[str]=None, maker: Optional[str]=None) -> Optional[int]:
        if not word_name or not explain:
            raise ValueError("word_name and explain required")
        if self.use_stub:
            # stub: 単純に擬似IDを返す
            return 1
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO terms (word_name, explain, category, maker) VALUES (?, ?, ?, ?);",
                    (word_name, explain, category, maker)
                )
                return cur.lastrowid
        except Exception:
            logger.exception("単語作成エラー")
            return None