# Model/wordlist_model.py
import logging
from typing import List, Dict, Optional

from Model.BaseModel import BaseModel  # 追加

logger = logging.getLogger(__name__)

# 読み仮名マップ（各行の先頭文字群）
YOMI_MAP = {
    'あ': ('あ', 'い', 'う', 'え', 'お'),
    'か': ('か', 'き', 'く', 'け', 'こ'),
    'さ': ('さ', 'し', 'す', 'せ', 'そ'),
    'た': ('た', 'ち', 'つ', 'て', 'と'),
    'な': ('な', 'に', 'ぬ', 'ね', 'の'),
    'は': ('は', 'ひ', 'ふ', 'へ', 'ほ'),
    'ま': ('ま', 'み', 'む', 'め', 'も'),
    'や': ('や', 'ゆ', 'よ'),
    'ら': ('ら', 'り', 'る', 'れ', 'ろ'),
    'わ': ('わ', 'を', 'ん'),
}

class WordListModel(BaseModel):
    """IT用語辞書のデータモデル（BaseModel の get_conn を利用）"""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)
        self._cache_all_terms: Optional[List[str]] = None

    def get_all_terms(self, force_refresh: bool = False) -> List[str]:
        if self._cache_all_terms is not None and not force_refresh:
            return self._cache_all_terms

        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT DISTINCT word_name FROM terms WHERE word_name IS NOT NULL ORDER BY word_name;")
                rows = cur.fetchall()
                terms = [row['word_name'] for row in rows]
                self._cache_all_terms = terms
                return terms
        except Exception as e:
            logger.exception("全件取得エラー")
            return []

    def get_terms_by_category(self, category: str) -> List[str]:
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

    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        try:
            with self.get_conn() as conn:
                cur = conn.execute("""
                    SELECT question_id, word_cloud_id, word_name, explain, tag, category, yomi
                    FROM terms
                    WHERE word_name = ?
                    LIMIT 1;
                """, (word_name,))
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("詳細取得エラー")
            return None

    def search_terms(self, query: str) -> List[str]:
        if not query:
            return self.get_all_terms()
        try:
            query_lower = query.lower()
            all_terms = self.get_all_terms()
            return [term for term in all_terms if query_lower in term.lower()]
        except Exception:
            logger.exception("検索処理エラー")
            return []

    def get_categories(self) -> List[str]:
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

    def get_terms_by_tag(self, tag: str) -> List[str]:
        """指定されたタグで用語をフィルタリング"""
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

    def is_db_available(self) -> bool:
        return self.db_path is not None

    def get_stats(self) -> Dict[str, int]:
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT COUNT(DISTINCT word_name) as cnt FROM terms WHERE word_name IS NOT NULL;")
                row = cur.fetchone()
                total = row['cnt'] if row and 'cnt' in row else (row[0] if row else 0)

                cur = conn.execute("""
                    SELECT category, COUNT(DISTINCT word_name) as count
                    FROM terms
                    WHERE word_name IS NOT NULL AND category IS NOT NULL
                    GROUP BY category;
                """)
                category_counts = {row['category']: row['count'] for row in cur.fetchall()}
                return {'total': total, 'by_category': category_counts}
        except Exception:
            logger.exception("統計取得エラー")
            return {'total': 0}
