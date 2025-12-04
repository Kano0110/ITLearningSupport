#ResultModel.py
from typing import Optional, List, Dict
from Model.BaseModel import BaseModel
import logging
 
logger = logging.getLogger(__name__)
 
class ResultModel(BaseModel):
    def __init__(self, db_path: Optional[str] = None, use_stub: bool = False):
        super().__init__(db_path=db_path)
        self.use_stub = use_stub
 
        # クイズ結果保持用（暫定）
        self.correct_count = 0
        self.total_questions = 0
        self.wronged_terms: List[Dict] = []
 
    # --- クイズ結果関連機能 ---
    def save_result(self, correct_count: int, total_questions: int, wronged_terms: List[Dict]):
        """クイズ結果を保存（暫定的にメモリ保持）"""
        self.correct_count = correct_count
        self.total_questions = total_questions
        self.wronged_terms = wronged_terms
 
    def get_result_summary(self) -> Dict:
        """結果の要約を返す"""
        percent = 0
        if self.total_questions > 0:
            percent = int((self.correct_count / self.total_questions) * 100)
        return {
            "correct_count": self.correct_count,
            "total_questions": self.total_questions,
            "percent": percent,
            "wronged_terms": self.wronged_terms
        }