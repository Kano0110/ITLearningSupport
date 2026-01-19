#Q_quiz_Model.py
import sqlite3
from datetime import datetime
from Model.BaseModel import BaseModel

class Q_Quiz_Model(BaseModel):
    def __init__(self, db_path=None):
        # BaseModelの初期化を利用してDBパスを解決
        super().__init__(db_path=db_path)

    def get_selected_terms(self, tag=None, category=None):
        """タグ・カテゴリで絞り込んだ単語ID一覧を取得"""
        with self.get_conn() as conn:
            query = "SELECT word_name FROM terms WHERE 1=1"
            params = []
            if tag:
                query += " AND tag = ?"
                params.append(tag)
            if category:
                query += " AND category = ?"
                params.append(category)
            # 削除されていないもの
            # query += " AND is_deleted = 0" 
            query += " ORDER BY RANDOM()"
            
            cur = conn.execute(query, params)
            return [row[0] for row in cur.fetchall()]

    def get_term_detail(self, term_id_or_name):
        with self.get_conn() as conn:
            if isinstance(term_id_or_name, int) or (isinstance(term_id_or_name, str) and term_id_or_name.isdigit()):
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
        """
        誤答選択肢を取得する。
        選択肢が足りなくなるのを防ぐため、少し多めに取得してからフィルタリングする。
        """
        with self.get_conn() as conn:
            distractors = []
            existing_ids = {correct_id}

            # 1. 優先: 同タグ・同カテゴリから取得
            # NOTE: SQLで厳密にlimitすると重複排除後に足りなくなるため、limit * 2 程度取得する
            base_sql = """
                SELECT id, word_name, explain FROM terms
                WHERE id != ? 
            """
            params = [correct_id]

            where_parts = []
            if tag:
                where_parts.append("tag = ?")
                params.append(tag)
            if category:
                where_parts.append("category = ?")
                params.append(category)

            sql = base_sql + (" AND " + " AND ".join(where_parts) if where_parts else "")
            sql += " ORDER BY RANDOM() LIMIT ?"
            # 少し多めに取る
            params.append(limit * 2)

            cur = conn.execute(sql, params)
            rows = cur.fetchall()
            for r in rows:
                if len(distractors) >= limit:
                    break
                if r[0] not in existing_ids:
                    distractors.append({"id": r[0], "name": r[1], "desc": r[2]})
                    existing_ids.add(r[0])

            # 2. 不足分を全体から補完
            if len(distractors) < limit:
                remain = limit - len(distractors)
                # ここでも多めに取る (remain * 3 + 5 くらい)
                fetch_count = remain * 3 + 5
                
                cur = conn.execute("""
                    SELECT id, word_name, explain FROM terms
                    WHERE id != ?
                    ORDER BY RANDOM() LIMIT ?
                """, (correct_id, fetch_count))
                rows2 = cur.fetchall()
                
                for r in rows2:
                    if len(distractors) >= limit:
                        break
                    if r[0] not in existing_ids:
                        distractors.append({"id": r[0], "name": r[1], "desc": r[2]})
                        existing_ids.add(r[0])

            return distractors[:limit]

    def record_answer(self, terms_uuid, selected_option, total_questions,
                      retry_checkflag=0, answered_at=None):
        """answers テーブルに回答履歴を保存"""
        if answered_at is None:
            answered_at = datetime.now().timestamp()
        try:
            with self.get_conn() as conn:
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
        except Exception as e:
            print(f"Error recording answer: {e}")

    def get_term_detail_by_id(self, term_id: int):
        """ID から単語詳細を取得する"""
        with self.get_conn() as conn:
            cur = conn.execute("""
                SELECT id, word_name, explain, tag, category
                FROM terms
                WHERE id = ?
            """, (term_id,))
            row = cur.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "desc": row[2],
            "tag": row[3],
            "category": row[4]
        }