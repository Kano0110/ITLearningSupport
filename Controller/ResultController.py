# Controller/ResultController.py
from typing import Optional
from Model.ResultModel import ResultModel
import tkinter as tk
import math
 
class ResultController:
    """結果画面を制御するコントローラ"""
 
    def __init__(self, app_controller, model: Optional[ResultModel] = None):
        self.app = app_controller
        self.model = model if model else ResultModel()
        self.view = None
 
        # クイズ結果保持用
        self.correct_count = 0
        self.total_questions = 0
        self.category = None
        self.tag = None
        self.wronged_terms = []
 
    def _ensure_view(self):
        """view が未生成なら生成する（遅延生成）。"""
        if self.view is None:
            from View.ResultView import ResultView
            self.view = ResultView(self.app.root, controller=self)
 
    def show(self):
        """画面表示（AppController から呼ばれる）。"""
        self._ensure_view()
        if hasattr(self.view, "show"):
            self.view.show()
 
    def hide(self):
        """現在のビューを非表示にする（AppController が呼ぶ）。"""
        if self.view and hasattr(self.view, "close"):
            self.view.close()
            
    def set_result(self, correct_count, total_questions, category, tag, wronged_terms):
        

        self.correct_count = correct_count
        self.total_questions = total_questions
        self.category = category
        self.tag = tag
        self.wronged_terms = wronged_terms or []
        

        percent = 0
        if total_questions > 0:
            percent = math.floor((correct_count / total_questions) * 100)

       

        # View に値を渡す
        self.view.set_result(
            correct_count=self.correct_count,
            total_questions=self.total_questions,
            percent=percent,
            category=self.category,
            tag=self.tag,
            wronged=self.wronged_terms
        )
    # --- 遷移系メソッド ---
    def return_wordlist(self):
        """単語一覧に戻る"""
        self.app.switch_view("wordlist")
 
    def return_qselect(self):
        """出題形式選択に戻る"""
        self.app.switch_view("qselect")
 
    def redo_quiz(self):
        """同じ条件でもう一度解く（暫定）"""
        self.app.switch_view("qselect")