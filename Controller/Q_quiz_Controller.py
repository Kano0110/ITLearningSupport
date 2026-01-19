#Q_quiz_Controller.py
from typing import List, Optional
import random
import time
from Model.Q_quiz_Model import Q_Quiz_Model

class Q_Quiz_Controller:
    def __init__(self, app_controller, model):
        self.app = app_controller
        self.model = model
        self.view = None  # 後で View を生成して接続
        self.term_list: List[str] = []
        self.mode: str = "hide_word"  # 'hide_word' or 'hide_desc'
        self.selected_tags = []
        self.selected_categories = []
        self.num_questions: int = 10

        self.current_index: int = 0
        self.correct_count: int = 0
        self.quiz_data: List[dict] = []
        self.wronged_terms: List[dict] = [] #間違えた単語
        self.review_terms = []              #見直しチェックをした単語

    def show(self):
        """AppController から呼ばれる表示処理"""
        if self.view is None:
            from View.Q_quiz_View import Q_Quiz_View
            self.view = Q_Quiz_View(self.app.root, self)
        self.view.show()

    def hide(self):
        self.timer_running = False
        if self.view:
            self.view.hide()

    def start(self, selected_terms: List[str], mode: str = "hide_word", num_questions: int = 10,selected_tags=None,selected_categories=None):
        self.mode = mode
        pool = list(selected_terms)
        random.shuffle(pool)

        self.num_questions = min(num_questions, len(pool))
        self.term_list = pool[:self.num_questions]

       # self.quiz_data = []

        self.selected_tags = selected_tags or []
        self.selected_categories = selected_categories or []

        for term_name in self.term_list:
            detail = self.model.get_term_detail(term_name)
            if not detail:
                continue
            distractors = self.model.get_distractors(
                detail["id"],
                tag=detail.get("tag"),
                category=detail.get("category")
            )

            self.quiz_data.append({
                "term": detail,
                "choices": self._build_choices(detail, distractors),
                "answered": False,
                "correct": None
            })




        self.current_index = 0
        self.correct_count = 0
        self._show_current_question()
            # タイマースタート
        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        """1秒ごとに時間を更新"""
        if not self.timer_running:
            return
    
        elapsed = time.time() - self.start_time
        if self.view:
            self.view.update_timer(elapsed)
    
        # 1秒後に再実行 (1000ms)
        self.app.root.after(1000, self._update_timer)

    def _build_choices(self, correct_term, distractors):
        choices = [correct_term] + distractors
        if len(choices) > 4:
            choices = choices[:4]
        random.shuffle(choices)
        return choices
        
    def _show_current_question(self):
        if self.current_index >= len(self.quiz_data):
            self._finish_quiz()
            return
        q = self.quiz_data[self.current_index]
        term = q["term"]
        choices = q["choices"]

        self.view.display_question(
            index=self.current_index + 1,
            total=len(self.quiz_data),
            term=term,
            choices=choices,
            mode=self.mode,
            tag=term.get("tag"),
            category=term.get("category")
        )


    def handle_answer(self, selected: dict):
        q = self.quiz_data[self.current_index]
        correct_term = q["term"]
        is_correct = (selected.get("id") == correct_term.get("id"))

        if self.mode == "hide_word":
            is_correct = selected.get("name") == correct_term.get("name")
        else:
            is_correct = selected.get("desc") == correct_term.get("desc")

        q["answered"] = True
        q["correct"] = is_correct
        if is_correct:
            self.correct_count += 1
        else:
            # 間違えた問題を記録
            print(f"Wrong answer recorded: {selected} vs correct {correct_term}")#デバッグ用
            self.wronged_terms.append({
                "term": correct_term.get("name"),
                "desc": correct_term.get("desc"),
                "user_answer": selected.get("name") or selected.get("desc")
            })
            self.timer_running = False

        self.view.show_result(is_correct, correct_term, selected)

    def next_question(self, review_flag=False):
        """次の問題へ進む"""

        if review_flag:     # チェックされていたら保存
            term = self.quiz_data[self.current_index]["term"]
            self.review_terms.append(term["id"])

        self.current_index += 1
        if self.current_index < len(self.quiz_data):
            self._show_current_question()
            #self.start_time = time.time()
            self.timer_running = True
            self._update_timer()
        else:
            self._finish_quiz()  # ← 最後の問題を終えたら終了処理へ

    def finish_quiz(self):
        """ユーザーが「回答を終了する」を押した場合"""
        self._finish_quiz()

    def _finish_quiz(self):
        """結果画面へ遷移"""
        #self.app.switch_view("home")
        self.timer_running = False # タイマーストップ
        elapsed_time = time.time() - self.start_time
            # AppControllerに結果画面表示を依頼
        if hasattr(self.app, "show_quiz_result"):
            self.app.show_quiz_result(
                correct_count=self.correct_count,
                total_questions=len(self.quiz_data),
                category=self.selected_categories,
                tag=self.selected_tags,
                wronged_terms=self.wronged_terms,
                elapsed_time=elapsed_time,
                selected_terms=self.term_list,
                mode=self.mode,
                num_questions=self.num_questions
            )
        else:
            # メソッドがない場合のフォールバック（ホームへ）
            print("Warning: show_quiz_result not implemented in AppController")
            self.app.switch_view("home")
