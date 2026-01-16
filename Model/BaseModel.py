"""
Model層: データベース接続の共通ロジック
"""
import sqlite3
import os
import sys
from typing import Optional
from contextlib import contextmanager

def get_db_path() -> str:
    """
    DB パスを取得
    start.py の定義に合わせる
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "word_master.db")

class BaseModel:
    """
    データベース接続と切断を管理する基底クラス
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            # start.py の定義に合わせる
            self.db_path = get_db_path()

        if not os.path.exists(self.db_path):
            print(f"警告: データベースが見つかりません: {self.db_path}")

    def get_conn(self) -> Optional[sqlite3.Connection]:
        """
        DBコネクションを取得（with文で使える）
        """
        return self._get_connection()

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

    def is_db_available(self) -> bool:
        return self.db_path is not None

# -------------------------
# 外部用: with文で使える get_conn 関数
# -------------------------
@contextmanager
def get_conn(db_path: Optional[str] = None):
    """
    外部から使える共通DB接続ヘルパー（with文対応）
    例:
        with get_conn(db_path) as conn:
            cur = conn.execute("SELECT ...")
    """
    base = BaseModel(db_path)
    conn = base.get_conn()
    try:
        if conn:
            yield conn
        else:
            yield None
    finally:
        if conn:
            conn.close()
