# Controller/ResultController.py
from typing import Optional
from Model.ResultModel import ResultModel
import tkinter as tk
from tkinter import messagebox

class WordEntryController:
    """"""

    def __init__(self, app_controller, model: Optional[ResultModel] = None):
        self.app = app_controller
        self.model = model if model else ResultModel()
        self.view = None

    def _ensure_view(self):
        """view が未生成なら生成する（遅延生成）。"""
        if self.view is None:
            from View.ResultView import ResultView
            self.view = ResultView(self.app.root, controller=self)

    def show(self):
        """画面表示（AppController から呼ばれる）。"""
        self._ensure_view()
        # View 側は self.view.pack などを内部で行っている想定
        if hasattr(self.view, "show"):
            self.view.show()

    def get_id_pass(self):
        """作成ボタン押下時の処理: 入力を取得して model.create_word を呼ぶ。"""
        

    def hide(self):
        """現在のビューを非表示にする（AppController が呼ぶ）。"""
        if self.view and hasattr(self.view, "close"):
            self.view.close()

    def ReturnWordView(self):
        """戻るボタン。wordlist に戻るよう AppController に切り替えを依頼する。"""
        #ここは変えんで良いかな
        # AppController が show_wordlist / switch_view("wordlist") を提供する想定
        if hasattr(self.app, "switch_view"):
            self.app.switch_view("wordlist")
        elif hasattr(self.app, "show_wordlist"):
            self.app.show_wordlist()
        else:
            # フォールバック: ウィンドウ閉じるだけ
            if self.view and hasattr(self.view, "close"):
                self.view.close()

    def ReturnFormatSellect(self):
        """絶賛制作中らしいので待つ"""
        if hasattr(self.app, "switch_view"):
            self.app.switch_view("wordlist")
        elif hasattr(self.app, "show_wordlist"):
            self.app.show_wordlist()
        else:
            # フォールバック: ウィンドウ閉じるだけ
            if self.view and hasattr(self.view, "close"):
                self.view.close()


    def RedoQuestion(self):
        """戻るボタン。wordlist に戻るよう AppController に切り替えを依頼する。"""
        if hasattr(self.app, "switch_view"):
                self.app.switch_view("wordlist")
        elif hasattr(self.app, "show_wordlist"):
                self.app.show_wordlist()
        else:
            # フォールバック: ウィンドウ閉じるだけ
            if self.view and hasattr(self.view, "close"):
                self.view.close()