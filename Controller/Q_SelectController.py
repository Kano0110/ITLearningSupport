# Controller/Q_SelectController.py
from typing import List, Optional, Callable
from Model.Q_SelectModel import Q_SelectModel

class Q_SelectController:
    def __init__(self, root_controller, model: Optional[Q_SelectModel] = None):
        """初期化
        
        Args:
            root_controller: AppController インスタンス
            model: Q_SelectModel インスタンス（デフォルト：新規作成）
        """
        self.app = root_controller
        self.model = model if model is not None else Q_SelectModel()
        
        # 状態管理
        self.current_category: Optional[str] = None
        self.current_tag: Optional[str] = None
        self.selected_terms: List[str] = []
        self.use_yomi_filter: bool = True
        
        # ビューと更新コールバック
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
        
        Args:
            callback: 呼び出し時に (tag_value, category_value) を受け取る関数
        """
        self.view_update_callback = callback
        # 登録時に現在の状態を通知
        try:
            self._notify_view_state()
        except Exception as e:
            print(f"Warning: set_view_update_callback failed: {e}")

    def _notify_view_state(self):
        """ビューに現在の状態を通知"""
        if self.view_update_callback:
            tag_display = self.current_tag if self.current_tag else "全て"
            category_display = self.current_category if self.current_category else "全て"
            self.view_update_callback(tag_display, category_display)

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
        """利用可能なカテゴリを取得"""
        return self.model.get_categories()

    def get_available_tags(self) -> List[str]:
        """利用可能なタグ一覧を取得"""
        return self.model.get_all_tags()

    def select_category(self, category: str):
        """カテゴリを選択
        
        Args:
            category: 選択されたカテゴリ（50音のいずれか）
        """
        self.current_category = category
        self.current_tag = None
        # yomi フィルタを使用して用語を取得
        self.selected_terms = self.model.get_terms_by_yomi(category)
        self._notify_view_state()

    def clear_category(self):
        """カテゴリ選択をクリア"""
        self.current_category = None
        self.current_tag = None
        self.selected_terms = self.model.get_all_terms()
        self._notify_view_state()

    def select_tag(self, tag: str):
        """タグを選択
        
        Args:
            tag: 選択されたタグ
        """
        self.current_tag = tag
        self.current_category = None
        self.selected_terms = self.model.get_terms_by_tag(tag)
        self._notify_view_state()

    def clear_tag(self):
        """タグ選択をクリア"""
        self.current_tag = None
        self.current_category = None
        self.selected_terms = self.model.get_all_terms()
        self._notify_view_state()

    def get_selected_terms(self) -> List[str]:
        """選択されている用語を取得
        
        Returns:
            現在フィルタリングされた用語リスト
        """
        return self.selected_terms

    def get_selection_summary(self) -> str:
        """選択サマリーを取得（表示用）
        
        Returns:
            選択内容を説明する文字列
        """
        if self.current_tag:
            return f"タグ: {self.current_tag} ({len(self.selected_terms)}個)"
        elif self.current_category:
            return f"カテゴリ: {self.current_category} ({len(self.selected_terms)}個)"
        else:
            return f"全て ({len(self.selected_terms)}個)"

    def start_quiz_important_order(self):
        """重要な順に出題を開始"""
        if not self.selected_terms:
            print("Error: No terms selected")
            return
        try:
            self.app.start_quiz(self.selected_terms, mode='important')
        except Exception as e:
            print(f"Error: Failed to start important quiz: {e}")

    def start_quiz_random(self):
        """ランダムに出題を開始"""
        if not self.selected_terms:
            print("Error: No terms selected")
            return
        try:
            self.app.start_quiz(self.selected_terms, mode='random')
        except Exception as e:
            print(f"Error: Failed to start random quiz: {e}")

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
