# WordbookModel.py
"""
Model層: 単語の詳細取得、および仮の「次へ/前へ」ロジック
"""
from Model.BaseModel import BaseModel
from typing import List, Dict, Optional

class WordBookModel(BaseModel):
    
    def __init__(self):
        super().__init__()
        # 状態データ（DB実装前の仮データ）
        self.current_word_id = 1
        self._words = {
             1: {"name": "ベルクマンの法則", "desc": "恒温動物においては、同じ種でも寒冷な地域に生息するものほど体重が大きく、近縁な種間では大型の種ほど寒冷な地域に生息する、という法則。"},
             2: {"name": "アレンの法則", "desc": "恒温動物の体の一部（耳、尾、四肢など）は、寒い地域に生息するものほど、熱放散を減らすために短くなるという法則。"},
             3: {"name": "ガウス分布", "desc": "左右対称な釣り鐘型の確率分布であり、自然現象や社会現象によく現れることから、正規分布とも呼ばれる。"}
         }
        self.max_id = max(self._words.keys())
        self.wN = self._words[1]["name"]
        self.wD = self._words[1]["desc"]
        
    def get_term_detail(self, word_name: str) -> Optional[Dict]:
        """
        特定の用語の詳細情報を取得
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

    # --- 以下は仮のWordbookModelから移行したロジック (DBベースに要修正) ---
    
    def fetch_word_data(self):
        """現在のIDに基づいてDBからデータを取得し、内部状態を更新する (仮実装)"""
        if self.current_word_id in self._words:
            data = self._words[self.current_word_id]
            self.wN = data["name"]
            self.wD = data["desc"]
            print(f"Model: ID {self.current_word_id} のデータを取得完了。")
            return True
        else:
            self.wN = "データなし"
            self.wD = "該当する単語IDが見つかりません。"
            return False

    def go_to_next_word(self):
        """次の単語IDへ進める (仮実装)"""
        if self.current_word_id < self.max_id:
            self.current_word_id += 1
            self.fetch_word_data()
        else:
            print("Model: これ以上、次の単語はありません。")

    def go_to_previous_word(self):
        """前の単語IDへ戻る (仮実装)"""
        if self.current_word_id > 1:
            self.current_word_id -= 1
            self.fetch_word_data()
        else:
            print("Model: これ以上、前の単語はありません。")
            