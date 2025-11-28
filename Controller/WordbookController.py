# WordbookController.py
import tkinter as tk
from tkinter import messagebox
from Model.WordbookModel import WordBookModel
from View.WordbookView import WordbookView
from typing import Optional, List

class WordbookController:
    
    def __init__(self, root_controller, book_model: WordBookModel):
        self.root_controller = root_controller
        self.book_model = book_model
        self.view = WordbookView(root_controller.root, self)
        self.current_word_name: Optional[str] = None 
        self.context_list: List[str] = [] # 表示順序用リスト

    def initialize_data_on_switch(self, word_name: str = None, context_list: List[str] = None):
        """
        Wordbook画面に切り替える際の初期化
        word_name: 表示する単語名
        context_list: 「次へ」「前へ」で使う単語リスト（Wordlistの絞り込み結果など）
        """
        # コンテキストリストの更新（渡された場合のみ）
        if context_list is not None:
            self.context_list = context_list
        
        # 指定がない場合、DBから最初の単語、もしくはリストの最初の単語を取得
        if not word_name:
            if self.context_list:
                word_name = self.context_list[0]
            else:
                word_name = self.book_model.get_first_word_name()
        
        self.current_word_name = word_name
        
        if not self.current_word_name:
            self.view.update_data(name="データなし", description="単語が登録されていません。", tag="", category="")
            return

        self._refresh_view()
            
    def _refresh_view(self):
        """現在の単語名でデータを再取得して表示更新"""
        if not self.current_word_name:
            return
            
        detail = self.book_model.get_term_detail(self.current_word_name)
        if detail:
            self.view.update_data(
                name=detail['name'],
                yomi=detail.get('yomi', ''),
                description=detail['desc'],
                tag=detail.get('tag', ''),
                category=detail.get('category', '')
            )
        else:
            self.view.update_data(name=self.current_word_name, description="詳細データが見つかりません。", tag="", category="")

    def show(self):
        self.view.pack(expand=True, fill='both')

    def hide(self):
        self.view.pack_forget()

    # --- 編集・削除ロジック ---

    def save_edits(self, name, yomi, description, tag, category):
        if not self.current_word_name:
            return
        
        detail = self.book_model.get_term_detail(self.current_word_name)
        if not detail or 'id' not in detail:
            messagebox.showerror("エラー", "更新対象の特定に失敗しました。")
            return

        word_id = detail['id']
        
        success = self.book_model.update_term(
            word_id=word_id,
            word_name=name,
            yomi=yomi,
            explain=description,
            tag=tag,
            category=category
        )

        if success:
            messagebox.showinfo("成功", "変更を保存しました。")
            
            # リスト内の名前も更新する必要があるが、簡易的に現在の名前を更新
            self.current_word_name = name 
            
            self.view.exit_edit_mode()
            self._refresh_view()
        else:
            messagebox.showerror("エラー", "保存に失敗しました。")

    def handle_delete_word(self):
        if not self.current_word_name:
            return

        if messagebox.askyesno("確認", f"本当に「{self.current_word_name}」を削除しますか？\nこの操作は取り消せません。"):
            detail = self.book_model.get_term_detail(self.current_word_name)
            if not detail or 'id' not in detail:
                messagebox.showerror("エラー", "削除対象の特定に失敗しました。")
                return
            
            success = self.book_model.delete_term(detail['id'])
            if success:
                messagebox.showinfo("完了", "削除しました。一覧画面に戻ります。")
                # 削除した単語をリストから除外する
                if self.current_word_name in self.context_list:
                    self.context_list.remove(self.current_word_name)
                self.handle_go_word_list()
            else:
                messagebox.showerror("エラー", "削除に失敗しました。")

    # --- 画面遷移 ---
    
    def handle_go_home(self):
        self.root_controller.switch_view("home")

    def handle_go_word_list(self):
        self.root_controller.switch_view("wordlist")

    # --- UI操作 ---
    
    def toggle_name_view(self):
        new_state = not self.view.name_is_visible
        
        # 修正: 読み仮名(yomi)も取得して渡す
        detail = self.book_model.get_term_detail(self.current_word_name)
        yomi = detail.get('yomi', '') if detail else ""
        
        # Viewのメソッド呼び出しに yomi を追加
        self.view.toggle_name_display(new_state, self.current_word_name, yomi)

    def toggle_description_view(self):
        new_state = not self.view.desc_is_visible
        detail = self.book_model.get_term_detail(self.current_word_name)
        desc = detail['desc'] if detail else ""
        self.view.toggle_description_display(new_state, desc)

    # --- 次へ/前へ 機能の実装 ---

    def handle_next_word(self):
        """次の単語へ移動"""
        if not self.current_word_name or not self.context_list:
            return
        
        try:
            # 現在の単語のインデックスを探す
            current_index = self.context_list.index(self.current_word_name)
            # 次のインデックス
            next_index = current_index + 1
            
            if next_index < len(self.context_list):
                next_word = self.context_list[next_index]
                # 自身のメソッドを呼んで表示切り替え（context_listはそのまま引き継ぐ）
                self.initialize_data_on_switch(next_word, self.context_list)
            else:
                messagebox.showinfo("情報", "これが最後の単語です。")
        except ValueError:
            # 現在の単語がリストに見つからない場合、先頭に戻るなどの処理
            if self.context_list:
                self.initialize_data_on_switch(self.context_list[0], self.context_list)

    def handle_previous_word(self):
        """前の単語へ移動"""
        if not self.current_word_name or not self.context_list:
            return
        
        try:
            current_index = self.context_list.index(self.current_word_name)
            prev_index = current_index - 1
            
            if prev_index >= 0:
                prev_word = self.context_list[prev_index]
                self.initialize_data_on_switch(prev_word, self.context_list)
            else:
                messagebox.showinfo("情報", "これが最初の単語です。")
        except ValueError:
            if self.context_list:
                self.initialize_data_on_switch(self.context_list[0], self.context_list)

    def cancel_edits(self):
        """編集キャンセル時の処理"""
        pass