# Model/WordbookModel.py
from typing import Optional, Dict
from Model.BaseModel import BaseModel
import logging

logger = logging.getLogger(__name__)

class WordbookModel(BaseModel):
    def __init__(self, db_path: Optional[str] = None, use_stub: bool = False):
        super().__init__(db_path=db_path)
        self.use_stub = use_stub
        # stub データ
        self._stub_words = {
            1: {"id":1, "name":"ベルクマンの法則", "desc":"..."},
            2: {"id":2, "name":"アレンの法則", "desc":"..."}
        }
        # 表示中の状態（インスタンス属性として初期化）
        self.current_word_id: Optional[int] = None
        self.wN: str = ""
        self.wD: str = ""

    def get_by_id(self, question_id: int) -> Optional[Dict]:
        if self.use_stub:
            return self._stub_words.get(question_id)
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT question_id AS id, word_name AS name, explain AS desc, tag, category, yomi FROM terms WHERE question_id = ? LIMIT 1;",
                    (question_id,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("ID検索エラー")
            return None

    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        if self.use_stub:
            for v in self._stub_words.values():
                if v["name"] == word_name:
                    return v
            return None
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT question_id AS id, word_name AS name, explain AS desc, tag, category, yomi FROM terms WHERE word_name = ? LIMIT 1;",
                    (word_name,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("詳細取得エラー")
            return None

    def update_term(self, question_id: int, word_name: str = None, explain: str = None,
                    tag: str = None, category: str = None) -> bool:
        if self.use_stub:
            if question_id in self._stub_words:
                w = self._stub_words[question_id]
                if word_name: w["name"] = word_name
                if explain: w["desc"] = explain
                return True
            return False
        try:
            with self.get_conn() as conn:
                conn.execute(
                    "UPDATE terms SET word_name = COALESCE(?, word_name), explain = COALESCE(?, explain), tag = COALESCE(?, tag), category = COALESCE(?, category) WHERE question_id = ?;",
                    (word_name, explain, tag, category, question_id)
                )
            return True
        except Exception:
            logger.exception("更新エラー")
            return False

    def delete_term(self, question_id: int) -> bool:
        if self.use_stub:
            return self._stub_words.pop(question_id, None) is not None
        try:
            with self.get_conn() as conn:
                conn.execute("DELETE FROM terms WHERE question_id = ?;", (question_id,))
            return True
        except Exception:
            logger.exception("削除エラー")
            return False

    # ---------- ここから表示用の補助メソッドを追加 ----------
    def fetch_word_data(self) -> Optional[Dict]:
        """current_word_id に基づき self.wN/self.wD を更新して返す"""
        if self.current_word_id is None:
            return None
        if self.use_stub:
            item = self._stub_words.get(self.current_word_id)
            if not item:
                return None
            self.wN = item.get("name", "")
            self.wD = item.get("desc", "")
            return item
        try:
            row = self.get_by_id(self.current_word_id)
            if not row:
                return None
            self.wN = row.get("name") or row.get("word_name") or ""
            self.wD = row.get("desc") or row.get("explain") or ""
            return row
        except Exception:
            logger.exception("fetch_word_data error")
            return None

    def _get_next_id(self, current_id: int) -> Optional[int]:
        """current_id より大きい最小の question_id を返す"""
        if self.use_stub:
            ids = sorted(self._stub_words.keys())
            for i in ids:
                if i > current_id:
                    return i
            return None
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT question_id FROM terms WHERE question_id > ? ORDER BY question_id ASC LIMIT 1;",
                    (current_id,)
                )
                row = cur.fetchone()
                return int(row["question_id"]) if row else None
        except Exception:
            logger.exception("_get_next_id error")
            return None

    def _get_prev_id(self, current_id: int) -> Optional[int]:
        """current_id より小さい最大の question_id を返す"""
        if self.use_stub:
            ids = sorted(self._stub_words.keys(), reverse=True)
            for i in ids:
                if i < current_id:
                    return i
            return None
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT question_id FROM terms WHERE question_id < ? ORDER BY question_id DESC LIMIT 1;",
                    (current_id,)
                )
                row = cur.fetchone()
                return int(row["question_id"]) if row else None
        except Exception:
            logger.exception("_get_prev_id error")
            return None

    def go_to_next_word(self) -> bool:
        """次の単語へ移動して fetch する。移動できれば True"""
        if self.current_word_id is None:
            return False
        next_id = self._get_next_id(self.current_word_id)
        if not next_id:
            return False
        self.current_word_id = next_id
        return self.fetch_word_data() is not None

    def go_to_previous_word(self) -> bool:
        """前の単語へ移動して fetch する。移動できれば True"""
        if self.current_word_id is None:
            return False
        prev_id = self._get_prev_id(self.current_word_id)
        if not prev_id:
            return False
        self.current_word_id = prev_id
        return self.fetch_word_data() is not None