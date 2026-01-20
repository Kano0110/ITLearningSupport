import sqlite3
import requests
import json
import uuid as uuid_lib
from datetime import datetime
import os
import sys

# ===== 設定 =====
SERVER_URL = 'http://10.18.20.132:5000'
API_KEY = 'ubuntu-sync-api-key-2024'

DB_PATH = r'C:\Users\user\desktop\zemi_github\ITLearningSupport\word_master.db'

class SyncClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        })
        
        if not os.path.exists(DB_PATH):
            print(f"❌ データベースが見つかりません: {DB_PATH}")
            print("DB_PATH を正しいパスに変更してください")
            sys.exit(1)
    
    def ensure_sync_table(self):
        """同期設定テーブルを作成"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def ensure_uuid(self):
        """全レコードにUUIDを付与"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # UUIDがない、または空のレコードを更新
        cursor.execute("""
            SELECT id FROM terms 
            WHERE uuid IS NULL OR uuid = ''
        """)

        
        records = cursor.fetchall()
        updated = 0
        
        for record in records:
            new_uuid = str(uuid_lib.uuid4())
            cursor.execute("""
                UPDATE terms 
                SET uuid = ?
                WHERE id = ?
            """, (new_uuid, record[0]))
            updated += 1
        
        conn.commit()
        conn.close()
        
        if updated > 0:
            print(f"✅ {updated}件のレコードにUUIDを生成しました")
        
        return updated
    
    def check_connection(self):
        """サーバー接続確認"""
        try:
            print(f"🔍 サーバー接続確認中: {SERVER_URL}")
            response = self.session.get(f"{SERVER_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ サーバー接続成功")
                print(f"   サーバー上の単語数: {data.get('terms_count', 0)}")
                return True
            else:
                print(f"❌ サーバーエラー: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ サーバーに接続できません")
            print(f"   Ubuntu VMが起動していることを確認してください")
            return False
        except Exception as e:
            print(f"❌ エラー: {e}")
            return False
    
    def get_local_terms(self):
        """ローカルの単語を取得"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM terms
            WHERE is_deleted = 0
            ORDER BY id
        """)
        
        terms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return terms
    
    def upload_terms(self):
        """サーバーにアップロード"""
        print("\n📤 アップロード開始...")
        
        terms = self.get_local_terms()
        print(f"   ローカル単語数: {len(terms)}")
        
        if not terms:
            print("   アップロードする単語がありません")
            return
        
        try:
            response = self.session.post(
                f"{SERVER_URL}/sync/upload",
                json={'terms': terms}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ アップロード成功")
                print(f"   新規: {result.get('new', 0)}件")
                print(f"   更新: {result.get('updated', 0)}件")
            else:
                print(f"❌ アップロード失敗: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ アップロードエラー: {e}")
    
    def download_terms(self):
        """サーバーからダウンロード"""
        print("\n📥 ダウンロード開始...")
        
        try:
            response = self.session.get(f"{SERVER_URL}/sync/download")
            
            if response.status_code == 200:
                data = response.json()
                server_terms = data.get('terms', [])
                print(f"   サーバー単語数: {len(server_terms)}")
                
                if server_terms:
                    self.save_terms(server_terms)
                else:
                    print("   ダウンロードする単語がありません")
            else:
                print(f"❌ ダウンロード失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
    
    def save_terms(self, server_terms):
        """ダウンロードした単語を保存"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        new_count = 0
        update_count = 0
        
        for term in server_terms:
            # 既存チェック
            cursor.execute("SELECT id FROM terms WHERE uuid = ?", (term['uuid'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                cursor.execute("""
                    UPDATE terms SET
                        word_name = ?,
                        explain = ?,
                        tag = ?,
                        category = ?,
                        yomi = ?
                    WHERE uuid = ?
                """, (
                    term.get('word_name'),
                    term.get('explain'),
                    term.get('tag'),
                    term.get('category'),
                    term.get('yomi'),
                    term['uuid']
                ))
                update_count += 1
            else:
                # 新規追加
                cursor.execute("""
                    INSERT INTO terms (
                        uuid, word_name, explain, tag, category, yomi,
                        sync_choice, is_deleted
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, 0)
                """, (
                    term['uuid'],
                    term.get('word_name', ''),
                    term.get('explain', ''),
                    term.get('tag'),
                    term.get('category'),
                    term.get('yomi')
                ))
                new_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ 保存完了")
        print(f"   新規: {new_count}件")
        print(f"   更新: {update_count}件")
    
    def sync(self):
        """完全同期を実行"""
        print("=" * 60)
        print("Word Master Sync - Ubuntu Server")
        print("=" * 60)
        print(f"サーバー: {SERVER_URL}")
        print(f"データベース: {DB_PATH}")
        print()
        
        # 準備
        self.ensure_sync_table()
        self.ensure_uuid()
        
        # 接続確認
        if not self.check_connection():
            print("\n同期を中止しました")
            return
        
        # アップロード
        self.upload_terms()
        
        # ダウンロード
        self.download_terms()
        
        # 完了
        print("\n" + "=" * 60)
        print("✅ 同期完了！")
        print("=" * 60)

def main():
    try:
        client = SyncClient()
        client.sync()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
    
    input("\n続行するにはEnterキーを押してください...")

if __name__ == "__main__":
    main()