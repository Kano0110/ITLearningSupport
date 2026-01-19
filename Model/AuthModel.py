import sqlite3
import hashlib
import os
from typing import Optional, Tuple
from .BaseModel import BaseModel

class AuthModel(BaseModel):
    """ユーザー認証（登録・ログイン）データモデル"""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)
        self._create_user_table()

    def _create_user_table(self):
        """ユーザー管理用テーブル作成"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login_id TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self.get_conn() as conn:
                conn.execute(create_sql)
                conn.commit()
        except Exception as e:
            print(f"Error creating users table: {e}")

    def _hash_password(self, password: str, salt: bytes = None) -> Tuple[str, str]:
        """パスワードのハッシュ化"""
        if salt is None:
            salt = os.urandom(16)
        else:
            if isinstance(salt, str):
                salt = bytes.fromhex(salt)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hash_obj.hex(), salt.hex()

    def register_user(self, login_id: str, password: str) -> bool:
        """新規登録"""
        if not login_id or not password:
            return False
            
        password_hash, salt_hex = self._hash_password(password)
        
        try:
            with self.get_conn() as conn:
                conn.execute(
                    "INSERT INTO users (login_id, password_hash, salt) VALUES (?, ?, ?)",
                    (login_id, password_hash, salt_hex)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Login ID {login_id} already exists.")
            return False
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    def login_user(self, login_id: str, password: str) -> bool:
        """ログイン認証"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT password_hash, salt FROM users WHERE login_id = ?",
                    (login_id,)
                )
                row = cur.fetchone()
                
                if row:
                    stored_hash = row['password_hash']
                    salt_hex = row['salt']
                    check_hash, _ = self._hash_password(password, salt_hex)
                    return check_hash == stored_hash
        except Exception as e:
            print(f"Login error: {e}")
            
        return False
    
    # 

    def check_user_exists(self, login_id: str) -> bool:
        """ログインIDが存在するか確認"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "SELECT id FROM users WHERE login_id = ?",
                    (login_id,)
                )
                return cur.fetchone() is not None
        except Exception as e:
            print(f"User check error: {e}")
            return False

    def update_password(self, login_id: str, new_password: str) -> bool:
        """パスワードを更新"""
        password_hash, salt_hex = self._hash_password(new_password)
        try:
            with self.get_conn() as conn:
                conn.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE login_id = ?",
                    (password_hash, salt_hex, login_id)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Password update error: {e}")
            return False