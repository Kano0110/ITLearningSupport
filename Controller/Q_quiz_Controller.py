#Q_quiz_Controller.py
from typing import List, Optional
import random
from Model.Q_quiz_Model import Q_Quiz_Model

class Q_Quiz_Controller:
    def __init__(self, app_controller, model):
        self.app = app_controller
        self.model = model
        self.view = None  # 後で View を生成して接続
        self.term_list: List[str] = []
        self.mode: str = "hide_word"  # 'hide_word' or 'hide_desc'
        self.tag: Optional[str] = None
        self.category: Optional[str] = None
        self.num_questions: int = 10

        self.current_index: int = 0
        self.correct_count: int = 0
        self.quiz_data: List[dict] = []

    def show(self):
        """AppController から呼ばれる表示処理"""
        if self.view is None:
            from View.Q_quiz_View import Q_Quiz_View
            self.view = Q_Quiz_View(self.app.root, self)
        self.view.show()

    def hide(self):
        if self.view:
            self.view.hide()

    def start(self, mode: str = "hide_word", tag: Optional[str] = None,
              category: Optional[str] = None, num_questions: int = 10):
        """出題開始"""
        self.mode = mode
        self.tag = tag
        self.category = category
        self.num_questions = num_questions

        self.term_list = self.model.get_selected_terms(tag=tag, category=category)
        random.shuffle(self.term_list)
        self.term_list = self.term_list[:num_questions]

        self.quiz_data = []
        for term in self.term_list:
            detail = self.model.get_term_detail(term)
            distractors = self.model.get_distractors(term, tag=tag, category=category)
            self.quiz_data.append({
                "term": detail,
                "choices": self._build_choices(detail, distractors),
                "answered": False,
                "correct": None
            })

        self.current_index = 0
        self.correct_count = 0
        self._show_current_question()

    def _build_choices(self, correct_term: dict, distractors: List[dict]) -> List[dict]:
        """正答とハズレ選択肢を混ぜてランダム化"""
        choices = [correct_term]
        for d in distractors:
            if self.mode == "hide_word":
                if d.get("name") != correct_term.get("name"):
                    choices.append(d)
            else:
                if d.get("desc") != correct_term.get("desc"):
                    choices.append(d)
            if len(choices) >= 4:
                break
        while len(choices) < 4:
            choices.append({"name": "（不足）", "desc": "（不足）"})
        random.shuffle(choices)
        return choices

    def _show_current_question(self):
        if self.current_index >= len(self.quiz_data):
            self._finish_quiz()
            return
        q = self.quiz_data[self.current_index]
        self.view.display_question(
            index=self.current_index + 1,
            total=len(self.quiz_data),
            term=q["term"],
            choices=q["choices"],
            mode=self.mode,
            tag=self.tag,
            category=self.category
        )

    def handle_answer(self, selected: dict):
        """選択肢がクリックされたときの処理"""
        q = self.quiz_data[self.current_index]
        correct_term = q["term"]
        is_correct = False
        if self.mode == "hide_word":
            is_correct = selected.get("name") == correct_term.get("name")
        else:
            is_correct = selected.get("desc") == correct_term.get("desc")

        q["answered"] = True
        q["correct"] = is_correct
        if is_correct:
            self.correct_count += 1

        self.view.show_result(is_correct, correct_term)

    def next_question(self):
        """次の問題へ進む"""
        self.current_index += 1
        self._show_current_question()

    def finish_quiz(self):
        """ユーザーが「回答を終了する」を押した場合"""
        self._finish_quiz()

    def _finish_quiz(self):
        """結果画面へ遷移"""
        self.app.switch_view("home")
    #    self.app.show_quiz_result(self.correct_count, len(self.quiz_data))