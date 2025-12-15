# Model/wordlist_model.py
"""IT用語辞書のデータモデル

用語の検索、フィルタリング、詳細情報の取得を提供します。
"""
import logging
from typing import List, Dict, Optional
from .BaseModel import BaseModel

logger = logging.getLogger(__name__)

# 読み仮名マップ（五十音の各行に対応する文字群）
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

class WordListModel(BaseModel):
    """IT用語辞書のデータモデル
    
    用語の取得、検索、フィルタリング機能を提供します。
    BaseModelのデータベース接続機能を利用します。
    """

    def __init__(self, db_path: Optional[str] = None):
        """初期化
        
        Args:
            db_path: データベースファイルパス（未指定時はデフォルト）
        """
        super().__init__(db_path=db_path)
        self._cache_all_terms: Optional[List[str]] = None

    def get_all_terms(self, force_refresh: bool = False) -> List[str]:
        """全用語を取得
        
        Args:
            force_refresh: キャッシュを無視して再取得する場合True
            
        Returns:
            全用語名のリスト（アルファベット順）
        """
        if self._cache_all_terms is not None and not force_refresh:
            return self._cache_all_terms

        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT word_name FROM terms "
                    "WHERE word_name IS NOT NULL "
                    "ORDER BY word_name;"
                )
                rows = cur.fetchall()
                terms = [row['word_name'] for row in rows]
                self._cache_all_terms = terms
                return terms
        except Exception:
            logger.exception("全件取得エラー")
            return []

    def _get_terms_by_filter(self, column: str, value: str) -> List[str]:
        """指定されたカラムと値で用語をフィルタリング（共通処理）
        
        Args:
            column: フィルタリングするカラム名
            value: フィルタ値
            
        Returns:
            フィルタリングされた用語名のリスト
        """
        if not value:
            return []
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    f"SELECT DISTINCT word_name FROM terms "
                    f"WHERE {column} = ? AND word_name IS NOT NULL "
                    f"ORDER BY word_name;",
                    (value,)
                )
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception(f"{column}別取得エラー")
            return []

    def get_terms_by_category(self, category: str) -> List[str]:
        """カテゴリで用語をフィルタリング
        
        Args:
            category: カテゴリ名
            
        Returns:
            該当する用語名のリスト
        """
        return self._get_terms_by_filter('category', category)

    def get_terms_by_yomi(self, yomi_key: str) -> List[str]:
        """読み仮名（五十音）で用語をフィルタリング
        
        Args:
            yomi_key: 五十音のキー（'あ'、'か'等）
            
        Returns:
            該当する用語名のリスト
        """
        if yomi_key not in YOMI_MAP:
            return []
        try:
            yomi_chars = YOMI_MAP[yomi_key]
            placeholders = ','.join('?' * len(yomi_chars))
            sql = (
                "SELECT DISTINCT word_name, yomi "
                "FROM terms "
                f"WHERE SUBSTR(yomi, 1, 1) IN ({placeholders}) "
                "AND word_name IS NOT NULL "
                "ORDER BY yomi, word_name;"
            )
            with self.get_conn() as conn:
                cur = conn.execute(sql, yomi_chars)
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("読み仮名別取得エラー")
            return []

    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        """用語の詳細情報を取得
        
        Args:
            word_name: 用語名
            
        Returns:
            用語の詳細情報（辞書形式）、見つからない場合はNone
        """
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT id, word_name, explain, tag, category, yomi "
                    "FROM terms "
                    "WHERE word_name = ? "
                    "LIMIT 1;",
                    (word_name,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception:
            logger.exception("詳細取得エラー")
            return None

    def search_terms(self, query: str) -> List[str]:
        """用語を検索（word_nameとyomiの両方で検索）
        
        Args:
            query: 検索クエリ
            
        Returns:
            マッチした用語名のリスト
        """
        if not query:
            return self.get_all_terms()
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT word_name "
                    "FROM terms "
                    "WHERE (word_name LIKE ? OR yomi LIKE ?) "
                    "AND word_name IS NOT NULL "
                    "ORDER BY word_name;",
                    (f'%{query}%', f'%{query}%')
                )
                return [row['word_name'] for row in cur.fetchall()]
        except Exception:
            logger.exception("検索処理エラー")
            return []

    # --- ヘルパーメソッド ---
    def get_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        return self.get_all_categories()

    def get_yomi_keys(self) -> List[str]:
        """五十音インデックス（YOMI_MAPのキー）を取得
        
        Returns:
            五十音のキーリスト（'あ'、'か'、'さ'等）
        """
        return list(YOMI_MAP.keys())

    def get_all_tags(self) -> List[str]:
        """データベースから全タグを取得
        
        Returns:
            タグ名のリスト（アルファベット順）
        """
        return self._get_distinct_values('tag')

    def get_terms_by_tag(self, tag: str) -> List[str]:
        """タグで用語をフィルタリング
        
        Args:
            tag: タグ名
            
        Returns:
            該当する用語名のリスト
        """
        return self._get_terms_by_filter('tag', tag)

    def get_all_categories(self) -> List[str]:
        """データベースから全カテゴリを取得"""
        return self._get_distinct_values('category')

    def _get_distinct_values(self, column: str) -> List[str]:
        """指定カラムのユニーク値を取得（共通処理）
        
        Args:
            column: カラム名
            
        Returns:
            ユニークな値のリスト
        """
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    f"SELECT DISTINCT {column} FROM terms "
                    f"WHERE {column} IS NOT NULL "
                    f"ORDER BY {column};"
                )
                rows = cur.fetchall()
                return [row[column] for row in rows if row[column]]
        except Exception:
            logger.exception(f"{column}一覧取得エラー")
            return []
    # --- ユーティリティ ---
    def is_db_available(self) -> bool:
        """データベースが利用可能かチェック
        
        Returns:
            データベースが利用可能な場合True
        """
        return self.db_path is not None

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得
        
        Returns:
            統計情報の辞書（total: 総数、by_category: カテゴリ別件数）
        """
        try:
            with self.get_conn() as conn:
                # 総用語数
                cur = conn.execute(
                    "SELECT COUNT(DISTINCT word_name) as cnt "
                    "FROM terms "
                    "WHERE word_name IS NOT NULL;"
                )
                row = cur.fetchone()
                total = row['cnt'] if row and 'cnt' in row else (row[0] if row else 0)

                # カテゴリ別件数
                cur = conn.execute(
                    "SELECT category, COUNT(DISTINCT word_name) as count "
                    "FROM terms "
                    "WHERE word_name IS NOT NULL AND category IS NOT NULL "
                    "GROUP BY category;"
                )
                category_counts = {row['category']: row['count'] for row in cur.fetchall()}
                return {'total': total, 'by_category': category_counts}
        except Exception:
            logger.exception("統計取得エラー")
            return {'total': 0}
