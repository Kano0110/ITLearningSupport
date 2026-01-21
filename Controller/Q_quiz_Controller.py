from typing import List
import random
import time
from Model.Q_quiz_Model import Q_Quiz_Model

class Q_Quiz_Controller:
    def __init__(self, app_controller, model):
        self.app = app_controller
        self.model = model
        self.view = None
        self.term_list: List[str] = []
        self.mode: str = "hide_word"
        self.selected_tags = []
        self.selected_categories = []
        self.num_questions: int = 10

        # タイマー関連
        self.total_elapsed = 0          # 純粋な解答時間（累積）
        self.question_start_time = 0    # 問題ごとの計測用

        self.display_elapsed = 0        # 表示用の累積時間
        self.display_start_time = 0     # 表示用の区間開始時間
        self.timer_running = False

        self.current_index: int = 0
        self.correct_count: int = 0
        self.quiz_data: List[dict] = []
        self.wronged_terms: List[dict] = []
        self.review_terms = []

    def show(self):
        if self.view is None:
            from View.Q_quiz_View import Q_Quiz_View
            self.view = Q_Quiz_View(self.app.root, self)
        self.view.show()

    def timer_start(self):
        self.timer_running = True
        self.display_start_time = time.time()  # 表示用タイマーの区間開始

    def timer_stop(self):
        self.timer_running = False
        # 表示用タイマーの区間を累積
        self.display_elapsed += time.time() - self.display_start_time

    def hide(self):
        self.timer_stop()
        if self.view:
            self.view.hide()

    def start(self, selected_terms: List[str], mode="hide_word",
              num_questions=10, selected_tags=None, selected_categories=None):

        self.mode = mode
        pool = list(selected_terms)
        random.shuffle(pool)

        self.num_questions = min(num_questions, len(pool))
        self.term_list = pool[:self.num_questions]

        # タイマー初期化
        self.total_elapsed = 0
        self.display_elapsed = 0
        self.display_start_time = time.time()
        self.question_start_time = time.time()

        self.selected_tags = selected_tags or []
        self.selected_categories = selected_categories or []

        self.quiz_data = []
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

        self.timer_start()
        self._update_timer()

    def _update_timer(self):
        if not self.timer_running:
            return

        now = time.time()
        elapsed = self.display_elapsed + (now - self.display_start_time)

        if self.view:
            self.view.update_timer(elapsed)

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

        # 問題開始時に計測用タイマーをリセット
        self.question_start_time = time.time()

    def handle_answer(self, selected: dict):
        q = self.quiz_data[self.current_index]
        correct_term = q["term"]

        # この問題にかかった時間を加算
        elapsed = time.time() - self.question_start_time
        self.total_elapsed += elapsed

        # 正誤判定
        if self.mode == "hide_word":
            is_correct = selected.get("name") == correct_term.get("name")
        else:
            is_correct = selected.get("desc") == correct_term.get("desc")

        q["answered"] = True
        q["correct"] = is_correct

        if is_correct:
            self.correct_count += 1
        else:
            self.wronged_terms.append({
                "term": correct_term.get("name"),
                "desc": correct_term.get("desc"),
                "user_answer": selected.get("name") or selected.get("desc")
            })

        self.timer_stop()
        self.view.show_result(is_correct, correct_term, selected)

    def next_question(self, review_flag=False):
        if review_flag:
            term = self.quiz_data[self.current_index]["term"]
            self.review_terms.append(term["id"])

        self.current_index += 1

        if self.current_index < len(self.quiz_data):
            self._show_current_question()
            self.timer_start()
            self._update_timer()
        else:
            self._finish_quiz()

    def finish_quiz(self):
        self._finish_quiz()

    def _finish_quiz(self):
        self.timer_stop()

        if hasattr(self.app, "show_quiz_result"):
            self.app.show_quiz_result(
                correct_count=self.correct_count,
                total_questions=len(self.quiz_data),
                category=self.selected_categories,
                tag=self.selected_tags,
                wronged_terms=self.wronged_terms,
                elapsed_time=self.total_elapsed,
                selected_terms=self.term_list,
                mode=self.mode,
                num_questions=self.num_questions
            )
        else:
            print("Warning: show_quiz_result not implemented in AppController")
            self.app.switch_view("home")