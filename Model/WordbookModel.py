# WordbookModel.py

# import mysql.connector
# from mysql.connector import Error

class WordbookModel:
    def __init__(self):
        # アプリケーションの状態データ
        self.current_word_id = 1 
        
        # 仮データ: DBから取得したと仮定する
        self._words = {
            1: {"name": "ベルクマンの法則", "desc": "恒温動物においては、同じ種でも寒冷な地域に生息するものほど体重が大きく、近縁な種間では大型の種ほど寒冷な地域に生息する、という法則。"},
            2: {"name": "アレンの法則", "desc": "恒温動物の体の一部（耳、尾、四肢など）は、寒い地域に生息するものほど、熱放散を減らすために短くなるという法則。"},
            3: {"name": "ガウス分布", "desc": "左右対称な釣り鐘型の確率分布であり、自然現象や社会現象によく現れることから、正規分布とも呼ばれる。"}
        }
        self.max_id = max(self._words.keys())
        
        # 現在表示中の単語データ
        self.wN = self._words[1]["name"]
        self.wD = self._words[1]["desc"]
        
        # DB接続設定（実際には使わないが構造を示す）
        self.db_config = {
            "host": "127.0.0.1",
            "user": "root",
            "password": "team8",
            "database": "wordbook"
        }

    def fetch_word_data(self):
        """現在のIDに基づいてDBからデータを取得し、内部状態を更新する"""
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
        """次の単語IDへ進める"""
        if self.current_word_id < self.max_id:
            self.current_word_id += 1
            self.fetch_word_data()
        else:
            print("Model: これ以上、次の単語はありません。")

    def go_to_previous_word(self):
        """前の単語IDへ戻る"""
        if self.current_word_id > 1:
            self.current_word_id -= 1
            self.fetch_word_data()
        else:
            print("Model: これ以上、前の単語はありません。")