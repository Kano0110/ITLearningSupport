# Controller/WordEntryController.py
from typing import Optional
from Model.WordEntryModel import WordEntryModel
import tkinter as tk
from tkinter import messagebox

class WordEntryController:
    """単語登録画面のコントローラ。View と Model の仲介を行う。"""

    def __init__(self, app_controller, model: Optional[WordEntryModel] = None):
        self.app = app_controller
        self.model = model if model else WordEntryModel()
        self.view = None

    def _ensure_view(self):
        """view が未生成なら生成する（遅延生成）。"""
        if self.view is None:
            from View.WordEntryView import WordEntryView
            self.view = WordEntryView(self.app.root, controller=self)

    def show(self):
        """画面表示（AppController から呼ばれる）。"""
        self._ensure_view()
        # View 側は self.view.pack などを内部で行っている想定
        if hasattr(self.view, "show"):
            self.view.show()

    def get_id_pass(self):
        """作成ボタン押下時の処理: 入力を取得して model.create_word を呼ぶ。"""
        self._ensure_view()
        name = self.view.get_name()
        explain = self.view.get_explain()
        try:
            new_id = self.model.create_word(name, explain, category=self.view.get_category(), maker=self.view.get_maker())
        except ValueError as e:
            self.view.show_error(str(e))
            return
        if new_id:
            # 追加成功: AppController に一覧更新を依頼
            if hasattr(self.app, "on_term_changed"):
                self.app.on_term_changed()
            self.view.show_success("単語を追加しました。")
            self.view.clear_inputs()
        else:
            self.view.show_error("追加に失敗しました。")

    def hide(self):
        """現在のビューを非表示にする（AppController が呼ぶ）。"""
        if self.view and hasattr(self.view, "close"):
            self.view.close()

    def create_close_window(self):
        """戻るボタン。Home に戻るよう AppController に切り替えを依頼する。"""
        # AppController が show_home / switch_view("home") を提供する想定
        if hasattr(self.app, "switch_view"):
            self.app.switch_view("home")
        elif hasattr(self.app, "show_home"):
            self.app.show_home()
        else:
            # フォールバック: ウィンドウ閉じるだけ
            if self.view and hasattr(self.view, "close"):
                self.view.close()

    def create_reset_window(self):
        """リセット確認ダイアログを表示し、ユーザーが肯定したら入力をクリアする。"""
        self._ensure_view()
        # シンプルな確認ダイアログ（Yes/No）
        if messagebox.askyesno("確認", "入力をリセットしますか？"):
            self.view.clear_inputs()