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

    def get_term_detail(self, term_id_or_name):
        with get_conn(self.db_path) as conn:
            if isinstance(term_id_or_name, int) or str(term_id_or_name).isdigit():
                cur = conn.execute("""
                    SELECT id, word_name, explain, tag, category
                    FROM terms
                    WHERE id = ?
                """, (int(term_id_or_name),))
            else:
                cur = conn.execute("""
                    SELECT id, word_name, explain, tag, category
                    FROM terms
                    WHERE word_name = ?
                """, (term_id_or_name,))
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

    def get_distractors(self, correct_id, tag=None, category=None, limit=3):
        with get_conn(self.db_path) as conn:
            distractors = []

            # 優先: 同タグ・同カテゴリ
            base_sql = """
                SELECT id, word_name, explain FROM terms
                WHERE id != ? AND is_deleted = 0
            """
            params = [correct_id]

            where_parts = []
            if tag:
                where_parts.append("tag = ?")
                params.append(tag)
            if category is not None:
                where_parts.append("category = ?")
                params.append(category)

            sql = base_sql + (" AND " + " AND ".join(where_parts) if where_parts else "")
            sql += " ORDER BY RANDOM() LIMIT ?"
            params.append(limit)

            cur = conn.execute(sql, params)
            rows = cur.fetchall()
            for r in rows:
                distractors.append({"id": r[0], "name": r[1], "desc": r[2]})

            # 足りなければ全体から補完
            if len(distractors) < limit:
                remain = limit - len(distractors)
                cur = conn.execute("""
                    SELECT id, word_name, explain FROM terms
                    WHERE id != ? AND is_deleted = 0
                    ORDER BY RANDOM() LIMIT ?
                """, (correct_id, remain))
                rows2 = cur.fetchall()
                # 既に入ってるIDを除外
                existing_ids = {d["id"] for d in distractors}
                for r in rows2:
                    if r[0] not in existing_ids:
                        distractors.append({"id": r[0], "name": r[1], "desc": r[2]})

            return distractors[:limit]

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
