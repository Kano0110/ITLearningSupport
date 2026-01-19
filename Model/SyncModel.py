import requests
import sqlite3
import uuid as uuid_lib
from typing import List, Dict, Optional
from .BaseModel import BaseModel

class SyncModel(BaseModel):
    """サーバー同期機能のデータモデル"""
    
    SERVER_URL = 'http://10.18.20.132:5000'
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path=db_path)
        self.token = None
        self._ensure_uuid()

    def _ensure_uuid(self):
        """全レコードにUUIDが付与されているか確認し、なければ生成"""
        try:
            with self.get_conn() as conn:
                cur = conn.execute("SELECT id FROM terms WHERE uuid IS NULL OR uuid = ''")
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        new_uuid = str(uuid_lib.uuid4())
                        conn.execute("UPDATE terms SET uuid = ? WHERE id = ?", (new_uuid, row['id']))
                    conn.commit()
        except Exception as e:
            print(f"UUID check error: {e}")

    def register_user_to_server(self, username, password) -> dict:
        """サーバーへ新規ユーザー登録リクエストを送信"""
        try:
            response = requests.post(
                f"{self.SERVER_URL}/auth/signup",
                json={'username': username, 'password': password},
                timeout=5
            )
            
            if response.status_code == 201:
                return {'success': True}
            elif response.status_code == 409:
                return {'success': False, 'error': 'このユーザー名はサーバーで既に使用されています'}
            else:
                return {'success': False, 'error': f"サーバーエラー: {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': f"通信エラー: {str(e)}"}

    def login(self, username, password) -> bool:
        """ログインしてトークン取得"""
        try:
            response = requests.post(
                f"{self.SERVER_URL}/auth/login",
                json={'username': username, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                return True
            else:
                print(f"Server Login Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def upload_data(self, target_uuids: list = None) -> Dict:
        """ローカルデータをサーバーへアップロード"""
        if not self.token:
            return {'error': 'サーバーにログインしていません'}

        try:
            with self.get_conn() as conn:
                conn.row_factory = sqlite3.Row
                
                if target_uuids and len(target_uuids) > 0:
                    placeholders = ','.join('?' * len(target_uuids))
                    sql = f"SELECT * FROM terms WHERE is_deleted = 0 AND uuid IN ({placeholders})"
                    cur = conn.execute(sql, target_uuids)
                else:
                    if target_uuids is not None and len(target_uuids) == 0:
                         return {'message': 'データが選択されていません', 'new': 0, 'updated': 0}
                    sql = "SELECT * FROM terms WHERE is_deleted = 0"
                    cur = conn.execute(sql)

                terms = [dict(row) for row in cur.fetchall()]

            if not terms:
                return {'message': 'アップロードするデータがありません', 'new': 0, 'updated': 0}

            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{self.SERVER_URL}/sync/upload",
                json={'terms': terms},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {'error': '認証切れです。再ログインしてください。'}
            else:
                return {'error': f"Server error: {response.status_code}"}

        except Exception as e:
            return {'error': str(e)}

    # ▼▼▼ 変更: サーバーからデータを取得するだけのメソッド（保存はしない） ▼▼▼
    def fetch_server_terms(self) -> Dict:
        """サーバーから単語リストを取得する（リスト表示用）"""
        if not self.token:
            return {'error': 'サーバーにログインしていません'}

        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{self.SERVER_URL}/sync/download",
                params={'limit': 1000},
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                # データリストを返す
                return {'status': 'success', 'terms': data.get('terms', [])}
            elif response.status_code == 401:
                return {'error': '認証切れです。再ログインしてください。'}
            else:
                return {'error': f"Fetch failed: {response.status_code}"}

        except Exception as e:
            return {'error': str(e)}

    # ▼▼▼ 変更: 受け取ったリストをローカルに保存するメソッド（ダウンロード実行用） ▼▼▼
    def import_to_local(self, terms: List[Dict]) -> Dict:
        """指定された単語データをローカルDBに保存（Upsert）"""
        new_cnt = 0
        upd_cnt = 0
        try:
            with self.get_conn() as conn:
                for term in terms:
                    uuid = term.get('uuid')
                    if not uuid: continue

                    # 既存チェック
                    cur = conn.execute("SELECT id FROM terms WHERE uuid = ?", (uuid,))
                    exists = cur.fetchone()

                    if exists:
                        conn.execute("""
                            UPDATE terms SET 
                                word_name=?, explain=?, tag=?, category=?, yomi=? 
                            WHERE uuid=?
                        """, (
                            term.get('word_name'), term.get('explain'),
                            term.get('tag'), term.get('category'),
                            term.get('yomi'), uuid
                        ))
                        upd_cnt += 1
                    else:
                        conn.execute("""
                            INSERT INTO terms (uuid, word_name, explain, tag, category, yomi)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            uuid, term.get('word_name'), term.get('explain'),
                            term.get('tag'), term.get('category'), term.get('yomi')
                        ))
                        new_cnt += 1
                conn.commit()
            return {'status': 'success', 'new': new_cnt, 'updated': upd_cnt}
        except Exception as e:
            return {'error': f"DB Save error: {e}"}

    # （旧メソッド互換性のため残す場合は、以下のように実装）
    def download_data(self) -> Dict:
        """[互換用] サーバーから全件取得して保存"""
        fetch_res = self.fetch_server_terms()
        if 'error' in fetch_res:
            return fetch_res
        return self.import_to_local(fetch_res['terms'])