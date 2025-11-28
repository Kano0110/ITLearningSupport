# Model/Q_SelectModel.py
import logging
from typing import List, Dict, Optional
from .BaseModel import BaseModel

logger = logging.getLogger(__name__)

# 読み仮名マップ（各行の先頭文字群）
# 清音 + 濁点 + 半濁点を含める
YOMI_MAP = {
    'あ': ('あ', 'い', 'う', 'え', 'お'),
    'か': ('か', 'き', 'く', 'け', 'こ', 'が', 'ぎ', 'ぐ', 'げ', 'ご'),
    'さ': ('さ', 'し', 'す', 'せ', 'そ', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ'),
    'た': ('た', 'ち', 'つ', 'て', 'と', 'だ', 'ぢ', 'づ', 'で', 'ど'),
    'な': ('な', 'に', 'ぬ', 'ね', 'の'),
    'は': ('は', 'ひ', 'ふ', 'へ', 'ほ', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'),
    'ま': ('ま', 'み', 'む', 'め', 'も'),
    'や': ('や', 'ゆ', 'よ'),
    'ら': ('ら', 'り', 'る', 'れ', 'ろ'),
    'わ': ('わ', 'を', 'ん'),
}

class Q_SelectModel(BaseModel):
    """問題選択画面のデータモデル"""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)

    def get_all_terms(self) -> List[str]:
        """全ての用語を取得"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT word_name FROM terms WHERE word_name IS NOT NULL ORDER BY word_name;")
                rows = cur.fetchall()
                terms = [row['word_name'] for row in rows]
                return terms
        except Exception:
            logger.exception("全件取得エラー")
            return []

    def get_terms_by_category(self, category: str) -> List[str]:
        """カテゴリで用語をフィルタリング"""
        if category not in YOMI_MAP:
            return []
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT word_name FROM terms WHERE category = ? AND word_name IS NOT NULL ORDER BY word_name;",
                    (category,)
                )
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("カテゴリ別取得エラー")
            return []

    def get_terms_by_yomi(self, category: str) -> List[str]:
        """読み仮名で用語をフィルタリング"""
        if category not in YOMI_MAP:
            return []
        try:
            placeholders = ','.join('?' * len(YOMI_MAP[category]))
            params = tuple(YOMI_MAP[category])
            sql = f"""
                SELECT DISTINCT word_name, yomi
                FROM terms
                WHERE SUBSTR(yomi, 1, 1) IN ({placeholders}) AND word_name IS NOT NULL
                ORDER BY yomi, word_name;
            """
            with self.get_conn() as conn:
                cur = conn.execute(sql, params)
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("読み仮名別取得エラー")
            return []

    def get_terms_by_tag(self, tag: str) -> List[str]:
        """タグで用語をフィルタリング"""
        if not tag:
            return []
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT word_name FROM terms WHERE tag = ? AND word_name IS NOT NULL ORDER BY word_name;",
                    (tag,)
                )
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("タグ別取得エラー")
            return []

    def get_categories(self) -> List[str]:
        """利用可能なカテゴリを取得"""
        return list(YOMI_MAP.keys())

    def get_all_tags(self) -> List[str]:
        """データベースから全タグを取得"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT tag FROM terms WHERE tag IS NOT NULL ORDER BY tag;")
                rows = cur.fetchall()
                tags = [row['tag'] for row in rows if row['tag']]
                return tags
        except Exception:
            logger.exception("タグ一覧取得エラー")
            return []

    def is_db_available(self) -> bool:
        """データベースが利用可能か確認"""
        return self.db_path is not None
