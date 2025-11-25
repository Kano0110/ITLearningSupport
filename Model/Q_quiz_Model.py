import sqlite3
from datetime import datetime
from Model.BaseModel import get_conn

class Q_Quiz_Model:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def get_selected_terms(self, tag=None, category=None):
        """タグ・カテゴリで絞り込んだ単語ID一覧を取得"""
        with get_conn(self.db_path) as conn:
            query = "SELECT id FROM terms WHERE 1=1"
            params = []
            if tag:
                query += " AND tag = ?"
                params.append(tag)
            if category:
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY RANDOM()"
            cur = conn.execute(query, params)
            return [row[0] for row in cur.fetchall()]

    def get_term_detail(self, term_id):
        """単語の詳細（名前・説明・タグ・カテゴリ）を取得"""
        with get_conn(self.db_path) as conn:
            cur = conn.execute("""
                SELECT id, word_name, explain, tag, category
                FROM terms
                WHERE id = ?
            """, (term_id,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "desc": row[2],
                    "tag": row[3],
                    "category": row[4]
                }
            return {}

    def get_distractors(self, correct_id, tag=None, category=None):
        """誤答選択肢（同じタグまたはカテゴリから）を取得"""
        with get_conn(self.db_path) as conn:
            query = """
                SELECT id, word_name, explain
                FROM terms
                WHERE id != ?
            """
            params = [correct_id]
            if tag:
                query += " AND tag = ?"
                params.append(tag)
            elif category:
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY RANDOM() LIMIT 10"
            cur = conn.execute(query, params)
            return [{"id": r[0], "name": r[1], "desc": r[2]} for r in cur.fetchall()]

    def record_answer(self, terms_uuid, selected_option, total_questions,
                      retry_checkflag=0, answered_at=None):
        """answers テーブルに回答履歴を保存"""
        if answered_at is None:
            answered_at = datetime.now().timestamp()  # UNIX時間で保存
        with get_conn(self.db_path) as conn:
            conn.execute("""
                INSERT INTO answers (
                    terms_uuid, selected_option, total_questions,
                    retry_checkflag, answered_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                terms_uuid,
                selected_option,
                total_questions,
                retry_checkflag,
                answered_at
            ))
            conn.commit()
