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
        
        # 修正: 画面表示時にプルダウンの中身を最新化する
        try:
            categories = self.model.get_categories()
            tags = self.model.get_all_tags()
            self.view.set_combo_values(categories, tags)
        except Exception as e:
            print(f"Warning: failed to load combo values: {e}")

        if hasattr(self.view, "show"):
            self.view.show()

    def get_id_pass(self):
        """作成ボタン押下時の処理: 入力を取得して model.create_word を呼ぶ。"""
        self._ensure_view()
        name = self.view.get_name()
        explain = self.view.get_explain()
        yomi = self.view.get_yomi()
        category = self.view.get_category()
        tag = self.view.get_tag()

        # バリデーション
        if not name:
            self.view.show_error("単語名を入力してください。")
            return
        if not explain:
            self.view.show_error("解説を入力してください。")
            return

        try:
            new_id = self.model.create_word(name, explain, yomi, category, tag)
        except ValueError as e:
            self.view.show_error(str(e))
            return

        if new_id:
            self.view.show_success("単語を追加しました。")
            # 入力欄をクリア（重要）
            self.view.clear_inputs()
            # 最新のカテゴリ/タグリストを再取得して反映
            try:
                categories = self.model.get_categories()
                tags = self.model.get_all_tags()
                self.view.set_combo_values(categories, tags)
            except Exception as e:
                print(f"Warning: failed to reload combo values: {e}")
        else:
            self.view.show_error("追加に失敗しました。")

    def hide(self):
        """現在のビューを非表示にする（AppController が呼ぶ）。"""
        if self.view and hasattr(self.view, "close"):
            self.view.close()

    def create_close_window(self):
        """戻るボタン。wordlist に戻るよう AppController に切り替えを依頼する。"""
        if hasattr(self.app, "switch_view"):
            self.app.switch_view("wordlist")
        elif hasattr(self.app, "show_wordlist"):
            self.app.show_wordlist()
        else:
            if self.view and hasattr(self.view, "close"):
                self.view.close()

    def create_reset_window(self):
        """リセット確認ダイアログを表示し、ユーザーが肯定したら入力をクリアする。"""
        self._ensure_view()
        if messagebox.askyesno("確認", "入力をリセットしますか？"):
            self.view.clear_inputs()