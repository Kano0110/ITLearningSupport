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
        self.tag: List[str] = []
        self.category: List[str] = []
        self.num_questions: int = 10

        self.current_index: int = 0
        self.correct_count: int = 0
        self.quiz_data: List[dict] = []
        self.wronged_terms: List[dict] = []

        # タイマー関連（全体時間のみ）
        self.total_elapsed = 0.0       # 累積経過時間
        self.last_start_time = None    # 再開時刻
        self.timer_running = False
        self._after_id = None

    def show(self):
        if self.view is None:
            from View.Q_quiz_View import Q_Quiz_View
            self.view = Q_Quiz_View(self.app.root, self)
        self.view.show()

    def hide(self):
        self._stop_timer()
        if self.view:
            self.view.hide()

    def start(self, selected_terms: List[str], mode: str = "hide_word", num_questions: int = 10):
        self.mode = mode
        pool = list(selected_terms)
        random.shuffle(pool)
        self.num_questions = min(num_questions, len(pool))
        self.term_list = pool[:self.num_questions]

        self.categories = []
        self.tags = []
        self.quiz_data = []

        for term_name in self.term_list:
            detail = self.model.get_term_detail(term_name)
            if not detail:
                continue

            cat = detail.get("category")
            tag = detail.get("tag")
            if cat and cat not in self.categories:
                self.categories.append(cat)
            if tag and tag not in self.tags:
                self.tags.append(tag)

            distractors = self.model.get_distractors(detail["id"], tag=tag, category=cat)
            self.quiz_data.append({
                "term": detail,
                "choices": self._build_choices(detail, distractors),
                "answered": False,
                "correct": None
            })

        self.category = self.categories
        self.tag = self.tags

        self.current_index = 0
        self.correct_count = 0
        self._show_current_question()

        # 全体タイマー開始
        self.total_elapsed = 0.0
        self.last_start_time = time.time()
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        if not self.timer_running:
            return

        now = time.time()
        elapsed = self.total_elapsed + (now - self.last_start_time)
        if self.view:
            self.view.update_timer(elapsed)

        self._after_id = self.app.root.after(1000, self._update_timer)

    def _stop_timer(self):
        """タイマー停止と予約キャンセル"""
        if self.timer_running and self.last_start_time:
            self.total_elapsed += time.time() - self.last_start_time
        self.timer_running = False
        self.last_start_time = None
        if self._after_id:
            self.app.root.after_cancel(self._after_id)
            self._after_id = None

    def _resume_timer(self):
        """タイマー再開"""
        self.last_start_time = time.time()
        self.timer_running = True
        self._update_timer()

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

        if self.mode == "hide_word":
            is_correct = selected.get("name") == correct_term.get("name")
        else:
            is_correct = selected.get("desc") == correct_term.get("desc")

        q["answered"] = True
        q["correct"] = is_correct

        if is_correct:
            self.correct_count += 1
        else:
            print(f"Wrong answer recorded: {selected} vs correct {correct_term}")
            self.wronged_terms.append({
                "term": correct_term.get("name"),
                "desc": correct_term.get("desc"),
                "user_answer": selected.get("name") or selected.get("desc")
            })

        # 回答後はタイマー停止
        self._stop_timer()

        self.view.show_result(is_correct, correct_term, selected)

    def next_question(self):
        self.current_index += 1
        if self.current_index < len(self.quiz_data):
            self._show_current_question()
            # 次の問題でタイマー再開
            self._resume_timer()
        else:
            self._finish_quiz()

    def finish_quiz(self):
        self._finish_quiz()

    def _finish_quiz(self):
        # 最終的な累積時間を確定
        self._stop_timer()
        elapsed_time = self.total_elapsed

        if hasattr(self.app, "show_quiz_result"):
            self.app.show_quiz_result(
                correct_count=self.correct_count,
                total_questions=len(self.quiz_data),
                category=self.category,
                tag=self.tag,
                wronged_terms=self.wronged_terms,
                elapsed_time=elapsed_time,
                selected_terms=self.term_list,
                mode=self.mode,
                num_questions=self.num_questions
            )
        else:
            print("Warning: show_quiz_result not implemented in AppController")
            self.app.switch_view("home")
