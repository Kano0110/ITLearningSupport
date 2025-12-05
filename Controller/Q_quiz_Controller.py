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
        self.wronged_terms: List[dict] = []

    def show(self):
        """AppController から呼ばれる表示処理"""
        if self.view is None:
            from View.Q_quiz_View import Q_Quiz_View
            self.view = Q_Quiz_View(self.app.root, self)
        self.view.show()

    def hide(self):
        if self.view:
            self.view.hide()

    def start(self, selected_terms: List[str], mode: str = "hide_word", num_questions: int = 10):
        self.mode = mode
        pool = list(selected_terms)
        random.shuffle(pool)
        self.num_questions = num_questions

        self.term_list = pool[:num_questions]

        self.quiz_data = []
        for term_name in self.term_list:
            detail = self.model.get_term_detail(term_name)
            distractors = self.model.get_distractors(detail["id"], tag=detail.get("tag"), category=detail.get("category"))
            self.quiz_data.append({
                "term": detail,
                "choices": self._build_choices(detail, distractors),
                "answered": False,
                "correct": None
            })

        if self.category is None:
            self.category = detail.get("category")
        if self.tag is None:
            self.tag = detail.get("tag")

        self.current_index = 0
        self.correct_count = 0
        self._show_current_question()

    def _build_choices(self, correct_term, distractors):
        choices = [correct_term] + distractors
        if len(choices) > 4:
            choices = choices[:4]
        random.shuffle(choices)
        return choices
        
    def _show_current_question(self):
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
        is_correct = False
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

        self.view.show_result(is_correct, correct_term)

    def next_question(self):
        """次の問題へ進む"""
        self.current_index += 1
        if self.current_index < len(self.quiz_data):
            self._show_current_question()
        else:
            self._finish_quiz()  # ← 最後の問題を終えたら終了処理へ

    def finish_quiz(self):
        """ユーザーが「回答を終了する」を押した場合"""
        self._finish_quiz()

    def _finish_quiz(self):
        """結果画面へ遷移"""
        #self.app.switch_view("home")
        self.app.show_quiz_result(
        correct_count=self.correct_count,
        total_questions=len(self.quiz_data),
        category=self.category,
        tag=self.tag,
        wronged_terms=self.wronged_terms,

#臨時追加
        selected_terms=self.term_list,
        mode=self.mode,
        num_questions=self.num_questions

    )
