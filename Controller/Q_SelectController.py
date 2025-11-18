# Controller/Q_selectController.py
from typing import List, Optional, Callable
from Model.Q_SelectModel import Q_SelectModel

class Q_SelectController:
    def __init__(self, root_controller, model: Optional[Q_SelectModel] = None):
        self.app = root_controller
        self.model = model if model is not None else Q_SelectModel()
        self.current_category: Optional[str] = None
        self.current_tag: Optional[str] = None
        self.use_yomi_filter: bool = True
        self.view = None  # 遅延生成
        self.selected_terms: List[str] = []

    def _ensure_view(self):
        """ビューが未生成の場合は生成"""
        if self.view is None:
            from View.Q_SelectView import Q_SelectView
            self.view = Q_SelectView(self.app.root, self)
            try:
                self.initialize()
            except Exception as e:
                print(f"Warning: ensure_view initialize failed: {e}")

    def initialize(self):
        """初期化処理"""
        if not self.model.is_db_available():
            return False
        return True

    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリを取得"""
        return self.model.get_categories()

    def get_available_tags(self) -> List[str]:
        """利用可能なタグ一覧を取得"""
        return self.model.get_all_tags()

    def select_category(self, category: str):
        """カテゴリを選択"""
        self.current_category = category
        self.current_tag = None
        if self.use_yomi_filter:
            self.selected_terms = self.model.get_terms_by_yomi(category)
        else:
            self.selected_terms = self.model.get_terms_by_category(category)

    def clear_category(self):
        """カテゴリ選択をクリア"""
        self.current_category = None
        self.selected_terms = self.model.get_all_terms()

    def select_tag(self, tag: str):
        """タグを選択"""
        self.current_tag = tag
        self.current_category = None
        self.selected_terms = self.model.get_terms_by_tag(tag)

    def clear_tag(self):
        """タグ選択をクリア"""
        self.current_tag = None
        self.selected_terms = self.model.get_all_terms()

    def get_selected_terms(self) -> List[str]:
        """選択されている用語を取得"""
        return self.selected_terms

    def start_quiz_with_selection(self):
        """選択された用語で問題を開始"""
        if not self.selected_terms:
            print("Error: No terms selected")
            return
        # AppController に quiz 画面を開くよう依頼
        try:
            self.app.start_quiz(self.selected_terms)
        except Exception as e:
            print(f"Error: Failed to start quiz: {e}")

    def go_to_home(self):
        """Home画面への遷移"""
        try:
            self.app.switch_view("home")
        except Exception as e:
            print(f"Error: Failed to switch to home: {e}")

    def show(self):
        """表示処理"""
        try:
            self._ensure_view()
        except Exception as e:
            print(f"Warning: show failed to ensure view: {e}")
        if hasattr(self.view, "show"):
            try:
                self.view.show()
            except Exception as e:
                print(f"Warning: view.show() failed: {e}")

    def hide(self):
        """非表示処理"""
        if hasattr(self.view, "hide"):
            self.view.hide()
