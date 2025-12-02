# Controller/Q_SelectController.py
from typing import List, Optional, Callable
from Model.Q_SelectModel import Q_SelectModel

class Q_SelectController:
    def __init__(self, root_controller, model: Optional[Q_SelectModel] = None):
        """初期化 (マルチタグ・マルチカテゴリ対応)
        
        root_controller: AppController インスタンス
        model: Q_SelectModel インスタンス
        """
        self.app = root_controller
        self.model = model if model is not None else Q_SelectModel()

        # 単一選択から複数選択へ変更
        self.selected_tags: set[str] = set()
        self.selected_categories: set[str] = set()  # DB の category カラム参照
        self.selected_terms: List[str] = []

        # ビューと更新コールバック (callback(terms, summary_text, tags_set, categories_set)) を想定
        self.view: Optional[object] = None
        self.view_update_callback: Optional[Callable] = None
        
    def _ensure_view(self):
        """ビューが未生成の場合は生成し、コールバックを登録"""
        if self.view is None:
            from View.Q_SelectView import Q_SelectView
            self.view = Q_SelectView(self.app.root, self)
            # ビューがコールバックを登録するまで待つ
            try:
                self.initialize()
            except Exception as e:
                print(f"Warning: ensure_view initialize failed: {e}")

    def set_view_update_callback(self, callback: Callable):
        """ビューが更新コールバックを登録するメソッド
        callback: (terms_list, summary_text, selected_tags, selected_categories) を受け取れる関数
        """
        self.view_update_callback = callback
        try:
            self._notify_view_state()
        except Exception as e:
            print(f"Warning: set_view_update_callback failed: {e}")

    def _notify_view_state(self):
        """ビューに現在の状態を通知"""
        if not self.view_update_callback:
            return
        summary = self.get_selection_summary()
        self.view_update_callback(list(self.selected_terms), summary, set(self.selected_tags), set(self.selected_categories))

    def initialize(self):
        """初期化処理"""
        if not self.model.is_db_available():
            print("Warning: Database not available")
            return False
        # 全用語を読み込む
        self.selected_terms = self.model.get_all_terms()
        self._notify_view_state()
        return True

    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリ (DB category) を取得"""
        return self.model.get_categories()

    def get_available_tags(self) -> List[str]:
        """利用可能なタグ一覧を取得"""
        return self.model.get_all_tags()

    # --- マルチ選択操作 ---
    def toggle_tag(self, tag: str):
        """タグの選択状態をトグル"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.add(tag)
        self._recompute_filtered_terms()

    def toggle_category(self, category: str):
        """カテゴリの選択状態をトグル (DB category)"""
        if category in self.selected_categories:
            self.selected_categories.remove(category)
        else:
            self.selected_categories.add(category)
        self._recompute_filtered_terms()

    def select_all_tags(self):
        """全タグを選択"""
        try:
            tags = self.model.get_all_tags()
            self.selected_tags = set(tags)
            self._recompute_filtered_terms()
        except Exception as e:
            print(f"Warning: select_all_tags failed: {e}")

    def select_all_categories(self):
        """全カテゴリを選択 (DB category)"""
        try:
            cats = self.model.get_categories()
            self.selected_categories = set(cats)
            self._recompute_filtered_terms()
        except Exception as e:
            print(f"Warning: select_all_categories failed: {e}")

    def clear_all(self):
        """全チェック解除"""
        self.selected_tags.clear()
        self.selected_categories.clear()
        self.selected_terms = self.model.get_all_terms()
        self._notify_view_state()

    def _recompute_filtered_terms(self):
        """選択されたタグ・カテゴリに基づき再計算"""
        self.selected_terms = self.model.get_terms_by_filters(list(self.selected_tags), list(self.selected_categories))
        self._notify_view_state()

    def get_selected_terms(self) -> List[str]:
        """選択されている用語を取得
        
        Returns:
            現在フィルタリングされた用語リスト
        """
        return self.selected_terms

    def get_selection_summary(self) -> str:
        """現在のマルチ選択状態のサマリー文字列"""
        parts = []
        if self.selected_tags:
            parts.append(f"タグ[{len(self.selected_tags)}]")
        if self.selected_categories:
            parts.append(f"カテゴリ[{len(self.selected_categories)}]")
        if not parts:
            parts.append("全て")
        return f"{' & '.join(parts)} : {len(self.selected_terms)}個"

    # 旧メソッド(重要順/ランダム)は現在未使用想定。必要なら復活させる。

    def start_quiz_hide_words(self):
        """単語を隠して出題を開始（解説のみを表示）"""
        if not self.selected_terms:
            print("Error: No terms selected")
            return
        try:
            self.app.start_quiz(self.selected_terms, mode='hide_words')
        except Exception as e:
            print(f"Error: Failed to start hide_words quiz: {e}")

    def start_quiz_hide_explanations(self):
        """解説を隠して出題を開始（単語のみを表示）"""
        if not self.selected_terms:
            print("Error: No terms selected")
            return
        try:
            self.app.start_quiz(self.selected_terms, mode='hide_explanations')
        except Exception as e:
            print(f"Error: Failed to start hide_explanations quiz: {e}")

    def go_to_home(self):
        """Home画面への遷移"""
        try:
            self.app.switch_view("home")
        except Exception as e:
            print(f"Error: Failed to switch to home: {e}")

    def show(self):
        """表示処理（AppController から呼ばれる）"""
        try:
            self._ensure_view()
        except Exception as e:
            print(f"Warning: show failed to ensure view: {e}")
        if self.view and hasattr(self.view, "show"):
            try:
                self.view.show()
            except Exception as e:
                print(f"Warning: view.show() failed: {e}")

    def hide(self):
        """非表示処理（AppController から呼ばれる）"""
        if self.view and hasattr(self.view, "hide"):
            try:
                self.view.hide()
            except Exception as e:
                print(f"Warning: view.hide() failed: {e}")
