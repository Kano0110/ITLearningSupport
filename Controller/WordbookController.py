#WordbookController.py
import tkinter as tk
from Model.WordbookModel import WordbookModel
from View.WordbookView import WordbookView

class WordbookController:
    def __init__(self, root_controller, model):
        # root_controller: AppControllerへの参照
        self.root_controller = root_controller
        self.model = model
        self.view = WordbookView(root_controller.root, self)

        # アプリ起動時はデータをロードしない (AppControllerからの指示を待つため)

    def load_term(self, word_name: str):
        """渡された単語名で詳細を取得して View に表示する"""
        try:
            detail = self.model.get_term_detail(word_name)
            if not detail:
                print(f"Warning: no detail found for '{word_name}'")
                return
            # detail のキーが 'id', 'name', 'desc' の形式を期待
            if 'id' in detail:
                try:
                    self.model.current_word_id = int(detail['id'])
                except Exception:
                    pass
            name = detail.get('name') or detail.get('word_name') or word_name
            desc = detail.get('desc') or detail.get('explain') or ""
            # 表示（view.update_data は既存実装）
            self.view.update_data(name, desc)
        except Exception as e:
            print(f"Error in load_term: {e}")

    def initialize_data_on_switch(self):
        """画面に切り替わったときに初期データ（ID 1）を強制的にロードする
           ただし既に current_word_id がセットされていれば変更しない。
        """
        # 既に current_word_id が有効なら初期ロードしない
        if getattr(self.model, "current_word_id", None):
            # current_word_id が設定済みなので既存データを表示する
            # model が wN/wD を保持していればそれを表示
            try:
                self.view.update_data(self.model.wN, self.model.wD)
            except Exception:
                pass
            return

        # 未設定なら最初の単語をロード
        try:
            self.model.current_word_id = 1
            # model 側に fetch_word_data() があることを想定
            if hasattr(self.model, "fetch_word_data"):
                self.model.fetch_word_data()
                self.view.update_data(self.model.wN, self.model.wD)
            else:
                # フォールバック: get_by_id を使って直接取得
                if hasattr(self.model, "get_by_id"):
                    detail = self.model.get_by_id(1)
                    if detail:
                        name = detail.get('name') or detail.get('word_name') or ""
                        desc = detail.get('desc') or detail.get('explain') or ""
                        self.view.update_data(name, desc)
        except Exception as e:
            print(f"Warning: initialize_data_on_switch failed: {e}")

    def show(self):
        """この画面を表示状態にする"""
        self.view.pack(expand=True, fill='both')

    def hide(self):
        """この画面を非表示状態にする"""
        self.view.pack_forget()

    # --- UI表示・非表示トグルロジック ---

    def toggle_name_view(self):
        new_state = not self.view.name_is_visible
        # model が wN を持つ前提で渡す（view が表示用に受け取る）
        current_name = getattr(self.model, "wN", None) or ""
        self.view.toggle_name_display(new_state, current_name)

    def toggle_description_view(self):
        new_state = not self.view.desc_is_visible
        current_desc = getattr(self.model, "wD", None) or ""
        self.view.toggle_description_display(new_state, current_desc)

    # --- データ切り替えロジック (次へ/前へ) ---

    def handle_next_word(self):
        if hasattr(self.model, "go_to_next_word"):
            self.model.go_to_next_word()
            # model が更新したデータを view に反映
            self.view.update_data(getattr(self.model, "wN", ""), getattr(self.model, "wD", ""))
        else:
            print("Warning: model has no go_to_next_word")

    def handle_previous_word(self):
        if hasattr(self.model, "go_to_previous_word"):
            self.model.go_to_previous_word()
            self.view.update_data(getattr(self.model, "wN", ""), getattr(self.model, "wD", ""))
        else:
            print("Warning: model has no go_to_previous_word")

    # --- 画面遷移プレースホルダー (Homeへ/一覧へ) ---

    def handle_go_home(self):
        # Homeへの遷移はAppControllerに依頼
        self.root_controller.switch_view("home")

    def handle_go_word_list(self):
        # 単語一覧への遷移はAppControllerに依頼
        self.root_controller.switch_view("wordlist")