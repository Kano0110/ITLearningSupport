# Controller/ResultController.py
from typing import Optional
from Model.ResultModel import ResultModel
import tkinter as tk
from tkinter import messagebox
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
        self.mode = None
 
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
            
    def set_result(self, correct_count, total_questions, category, tag, wronged_terms, mode, selected_terms, num_questions, elapsed_time=None):
        self._ensure_view()

        self.correct_count = correct_count
        self.total_questions = total_questions
        self.category = category
        self.tag = tag
        #self.wronged_terms = wronged_terms or []
        self.wronged_terms = [item["term"] for item in (wronged_terms or [])]

        #臨時追加
        self.selected_terms = selected_terms
        self.mode = mode
        self.num_questions = num_questions
        self.elapsed_time = elapsed_time      

        percent = 0
        if total_questions > 0:
            percent = math.floor((correct_count / total_questions) * 100)
            self.elapsed_time = elapsed_time

        # View に値を渡す
        self.view.set_result(
            correct_count=self.correct_count,
            total_questions=self.total_questions,
            percent=percent,
            category=self.category,
            tag=self.tag,
            wronged=self.wronged_terms,
            elapsed_time=self.elapsed_time
        )
    # --- 遷移系メソッド ---
    def return_wordlist(self):
        """単語一覧に戻る"""
        self.app.switch_view("wordlist")
 
    def return_qselect(self):
        """出題形式選択に戻る"""
        self.app.switch_view("qselect")
 
    def redo_quiz(self):
        """同じ条件でもう一度解く"""
        # 新しい quiz controller を作る
        quiz = self.app._create_quiz_controller()

        # 現在の画面を閉じる
        self.app.current_controller.hide()

        # コントローラを差し替え
        self.app.current_controller = quiz
        quiz.show()

        # 同じ条件でクイズを開始
        quiz.start(
            selected_terms=self.selected_terms,
            mode=self.mode,
            num_questions=self.num_questions,
            selected_tags=self.tag,
            selected_categories=self.category
        )

    def start_review_quiz(self):
        """見直し対象の問題だけで再クイズを開始する"""

        # Q_Quiz_Controller が保持している review_terms を取得
        quiz_ctrl = self.app._controller_cache.get("quiz")

        if not quiz_ctrl or not getattr(quiz_ctrl, "review_terms", None):
            messagebox.showinfo("見直し問題", "見直し対象の問題がありません。")
            return

        # term_id → term_name に変換
        selected_terms = []
        for term_id in quiz_ctrl.review_terms:
            detail = quiz_ctrl.model.get_term_detail_by_id(term_id)
            if detail:
                selected_terms.append(detail["name"])

        if not selected_terms:
            print("見直し対象の単語が取得できませんでした。")
            return

        # 新しいクイズコントローラを作成して開始
        new_quiz = self.app._create_quiz_controller()

        # 画面切り替え
        self.app.current_controller.hide()
        self.app.current_controller = new_quiz
        new_quiz.show()

        # 見直し問題だけでクイズ開始
        new_quiz.start(
            selected_terms=selected_terms,
            mode=self.mode,
            num_questions=len(selected_terms),
            selected_tags=self.tag,
            selected_categories=self.category
        )