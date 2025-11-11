#WordModel.py
"""
Model層: データベースアクセスとビジネスロジックを担当
"""
import sqlite3
import os
from typing import List, Dict, Optional, Tuple

DB_FILE = "word_master.db"

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

# DBパス候補
DB_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), '..', DB_FILE),
    os.path.join(os.path.dirname(__file__), DB_FILE),
    DB_FILE
]


class WordListModel(BaseModel):
    """IT用語辞書のデータモデル"""
    
    def __init__(self):
        super().__init__()
        self._cache_all_terms: Optional[List[str]] = None  # 全件キャッシュ
     
    def _find_db_path(self) -> Optional[str]:
        """DBファイルのパスを検索"""
        for p in DB_CANDIDATES:
            if os.path.exists(p):
                return p
        return None
    
    def _get_connection(self) -> Optional[sqlite3.Connection]:
        """DBコネクションを取得"""
        if not self.db_path:
            return None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 辞書形式で取得
            return conn
        except Exception as e:
            print(f"DB接続エラー: {e}")
            return None
    
    def get_all_terms(self, force_refresh: bool = False) -> List[str]:
        """
        全ての用語を取得（キャッシュ機能付き）
        
        Args:
            force_refresh: Trueの場合、キャッシュを無視して再取得
            
        Returns:
            用語名のリスト
        """
        if self._cache_all_terms is not None and not force_refresh:
            return self._cache_all_terms
        
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            sql = "SELECT DISTINCT word_name FROM terms WHERE word_name IS NOT NULL ORDER BY word_name;"
            cur.execute(sql)
            rows = cur.fetchall()
            terms = [row['word_name'] for row in rows]
            self._cache_all_terms = terms
            return terms
        except Exception as e:
            print(f"全件取得エラー: {e}")
            return []
        finally:
            conn.close()
    
    def get_terms_by_category(self, category: str) -> List[str]:
        """
        カテゴリ（五十音行）で絞り込んだ用語を取得
        
        Args:
            category: カテゴリ名（'あ', 'か', 'さ'など）
            
        Returns:
            用語名のリスト
        """
        if category not in YOMI_MAP:
            return []
        
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            sql = """
                SELECT DISTINCT word_name 
                FROM terms 
                WHERE category = ? AND word_name IS NOT NULL
                ORDER BY word_name;
            """
            cur.execute(sql, (category,))
            rows = cur.fetchall()
            return [row['word_name'] for row in rows]
        except Exception as e:
            print(f"カテゴリ別取得エラー: {e}")
            return []
        finally:
            conn.close()
    
    def get_terms_by_yomi(self, category: str) -> List[str]:
        """
        読み仮名（yomi）で絞り込んだ用語を取得
        
        Args:
            category: カテゴリ名（'あ', 'か', 'さ'など）
            
        Returns:
            用語名のリスト
        """
        if category not in YOMI_MAP:
            return []
        
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            # yomiカラムの先頭文字がYOMI_MAPの文字のいずれかに一致
            placeholders = ','.join('?' * len(YOMI_MAP[category]))
            params = tuple(YOMI_MAP[category])
            sql = f"""
                SELECT DISTINCT word_name, yomi
                FROM terms 
                WHERE SUBSTR(yomi, 1, 1) IN ({placeholders}) AND word_name IS NOT NULL
                ORDER BY yomi, word_name;
            """
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [row['word_name'] for row in rows]
        except Exception as e:
            print(f"読み仮名別取得エラー: {e}")
            return []
        finally:
            conn.close()
    
    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        """
        特定の用語の詳細情報を取得
        
        Args:
            word_name: 用語名
            
        Returns:
            用語の詳細情報（辞書形式）、見つからない場合はNone
        """
        conn = self._get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            sql = """
                SELECT question_id, word_cloud_id, word_name, explain, tag, category, yomi
                FROM terms 
                WHERE word_name = ?
                LIMIT 1;
            """
            cur.execute(sql, (word_name,))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"詳細取得エラー: {e}")
            return None
        finally:
            conn.close()
    
    def search_terms(self, query: str) -> List[str]:
        """
        用語を検索（部分一致）
        
        Args:
            query: 検索クエリ
            
        Returns:
            マッチした用語名のリスト
        """
        if not query:
            return self.get_all_terms()
        
        query_lower = query.lower()
        all_terms = self.get_all_terms()
        return [term for term in all_terms if query_lower in term.lower()]
    
    def get_categories(self) -> List[str]:
        """
        利用可能なカテゴリ（五十音行）のリストを取得
        
        Returns:
            カテゴリのリスト
        """
        return list(YOMI_MAP.keys())
    
    def is_db_available(self) -> bool:
        """
        データベースが利用可能かチェック
        
        Returns:
            利用可能ならTrue
        """
        return self.db_path is not None
    
    def get_stats(self) -> Dict[str, int]:
        """
        統計情報を取得
        
        Returns:
            統計情報の辞書（総用語数、カテゴリ別の用語数など）
        """
        conn = self._get_connection()
        if not conn:
            return {'total': 0}
        
        try:
            cur = conn.cursor()
            
            # 総用語数
            cur.execute("SELECT COUNT(DISTINCT word_name) FROM terms WHERE word_name IS NOT NULL;")
            total = cur.fetchone()[0]
            
            # カテゴリ別の用語数
            cur.execute("""
                SELECT category, COUNT(DISTINCT word_name) as count 
                FROM terms 
                WHERE word_name IS NOT NULL AND category IS NOT NULL
                GROUP BY category;
            """)
            category_counts = {row['category']: row['count'] for row in cur.fetchall()}
            
            return {
                'total': total,
                'by_category': category_counts
            }
        except Exception as e:
            print(f"統計取得エラー: {e}")
            return {'total': 0}
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            sql = """
                INSERT INTO terms (word_name, yomi, explain, tag, category)
                VALUES (?, ?, ?, ?, ?);
            """
            cur.execute(sql, (word_name, yomi, explain, tag, category))
            conn.commit()
            
            # キャッシュをクリア
            self._cache_all_terms = None
            return True
        except Exception as e:
            print(f"用語追加エラー: {e}")
            return False
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            sql = """
                UPDATE terms 
                SET yomi = ?, explain = ?, tag = ?, category = ?
                WHERE word_name = ?;
            """
            cur.execute(sql, (yomi, explain, tag, category, word_name))
            conn.commit()
            
            # キャッシュをクリア
            self._cache_all_terms = None
            return True
        except Exception as e:
            print(f"用語更新エラー: {e}")
            return False
        finally:
            conn.close()
    
    def delete_term(self, word_name: str) -> bool:
        """
        用語を削除
        
        Args:
            word_name: 単語名
            
        Returns:
            成功した場合True
        """
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            sql = "DELETE FROM terms WHERE word_name = ?;"
            cur.execute(sql, (word_name,))
            conn.commit()
            
            # キャッシュをクリア
            self._cache_all_terms = None
            return True
        except Exception as e:
            print(f"用語削除エラー: {e}")
            return False
        finally:
            conn.close()
