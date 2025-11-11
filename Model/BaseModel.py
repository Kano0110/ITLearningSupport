# Model/BaseModel.py

import sqlite3
import os
from typing import Optional, List, Dict
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

DB_FILE = "word_master.db"

DB_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), '..', DB_FILE),
    os.path.join(os.path.dirname(__file__), DB_FILE),
    DB_FILE
]

class BaseModel:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self._find_db_path()
        if not self.db_path:
            raise ValueError("データベースファイル 'word_master.db' が見つかりません。")

    def _find_db_path(self) -> Optional[str]:
        for p in DB_CANDIDATES:
            abs_p = os.path.abspath(p)
            if os.path.exists(abs_p):
                return abs_p
        return None

    @contextmanager
    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.exception("DB operation failed")
            raise
        finally:
            conn.close()

    def fetchall(self, sql, params=()):
        with self.get_conn() as conn:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def execute(self, sql, params=()):
        with self.get_conn() as conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid

    def exists(self, table_name: str) -> bool:
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        rows = self.fetchall(sql, (table_name,))
        return len(rows) > 0