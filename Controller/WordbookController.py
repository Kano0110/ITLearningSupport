# WordbookController.py
import tkinter as tk
from Model.WordbookModel import WordbookModel
from View.WordbookView import WordbookView

class WordbookController:
    def __init__(self, root_controller, model):
        # root_controller: AppControllerへの参照
        self.root_controller = root_controller
        self.model = model
        self.view = WordbookView(root_controller.root, self)

        # 現在表示している単語の detail を保持する（トグルや再表示で使う）
        self._current_detail = None

    # --- 正規化ユーティリティ ---
    def _normalize_tag(self, raw_tag):
        """raw_tag を整形して '未設定' か 'a, b' の形式で返す"""
        if raw_tag is None:
            return "未設定"
        s = str(raw_tag).strip()
        if not s:
            return "未設定"
        parts = [p.strip() for p in s.replace('、', ',').split(',') if p.strip()]
        return ", ".join(parts) if parts else "未設定"

    def _normalize_category(self, raw_cat):
        """raw_cat を整形して '未設定' か trimmed value を返す"""
        if raw_cat is None:
            return "未設定"
        s = str(raw_cat).strip()
        return s if s else "未設定"

    # --- current detail のセットと view 反映 ---
    def _set_current_detail(self, detail):
        """detail を controller の現在表示データとして保持し、view へ反映する"""
        self._current_detail = detail or {}
        name = self._current_detail.get('name') or self._current_detail.get('word_name') or ""
        desc = self._current_detail.get('desc') or self._current_detail.get('explain') or ""
        raw_tag = self._current_detail.get('tag') or self._current_detail.get('tags') or None
        raw_cat = self._current_detail.get('category') or self._current_detail.get('cat') or None
        tag = self._normalize_tag(raw_tag)
        category = self._normalize_category(raw_cat)
        try:
            self.view.update_data(name, desc, tag=tag, category=category)
        except TypeError:
            self.view.update_data(name, desc)

    # --- 単語ロード ---
    def load_term(self, word_name: str):
        """指定された単語名の詳細を取得して View を常に現在単語に合わせて更新する"""
        print(f"DEBUG: load_term called for {word_name}")
        try:
            detail = self.model.get_term_detail(word_name)
            print("DEBUG: detail:", detail)

            if not detail:
                print(f"Warning: no detail found for '{word_name}'")
                # 明示的に未設定 detail を保持して反映
                self._set_current_detail({'name': word_name, 'desc': '', 'tag': None, 'category': None})
                return

            # id の取り扱い（互換処理）
            if 'id' in detail:
                try:
                    self.model.current_word_id = int(detail['id'])
                except Exception:
                    pass
            elif 'question_id' in detail:
                try:
                    self.model.current_word_id = int(detail['question_id'])
                except Exception:
                    pass

            # current detail をセットして view に反映する
            self._set_current_detail(detail)
        except Exception as e:
            print(f"Error in load_term: {e}")

    # --- 画面切替時の初期データロード ---
    def initialize_data_on_switch(self):
        """画面に切り替わったときに初期データ（ID 1）を強制的にロードする
           ただし既に current_word_id がセットされていればそれを表示する
        """
        if getattr(self.model, "current_word_id", None):
            try:
                # 可能ならモデルの保持値から detail を作る
                detail = {
                    'name': getattr(self.model, "wN", "") or "",
                    'desc': getattr(self.model, "wD", "") or "",
                    'tag': getattr(self.model, "wTag", None),
                    'category': getattr(self.model, "wCat", None)
                }
                self._set_current_detail(detail)
            except Exception:
                pass
            return

        try:
            self.model.current_word_id = 1
            if hasattr(self.model, "fetch_word_data"):
                self.model.fetch_word_data()
                detail = {
                    'name': getattr(self.model, "wN", "") or "",
                    'desc': getattr(self.model, "wD", "") or "",
                    'tag': getattr(self.model, "wTag", None),
                    'category': getattr(self.model, "wCat", None)
                }
                self._set_current_detail(detail)
            else:
                if hasattr(self.model, "get_by_id"):
                    detail = self.model.get_by_id(1)
                    if detail:
                        self._set_current_detail(detail)
        except Exception as e:
            print(f"Warning: initialize_data_on_switch failed: {e}")

    # --- 表示制御 ---
    def show(self):
        self.view.pack(expand=True, fill='both')

    def hide(self):
        self.view.pack_forget()

    # --- UI表示・非表示トグルロジック ---
    def toggle_name_view(self):
        """トグル時は必ず現在の detail から name を取り出して渡す"""
        new_state = not self.view.name_is_visible
        name = ""
        if getattr(self, "_current_detail", None):
            name = self._current_detail.get('name') or self._current_detail.get('word_name') or ""
        else:
            # fallback: model から取得を試みる
            try:
                if getattr(self.model, "current_word_id", None) and hasattr(self.model, "get_by_id"):
                    d = self.model.get_by_id(self.model.current_word_id) or {}
                    name = d.get('name') or d.get('word_name') or ""
                elif hasattr(self.model, "get_current_detail"):
                    d = self.model.get_current_detail() or {}
                    name = d.get('name') or d.get('word_name') or ""
            except Exception:
                name = getattr(self.model, "wN", "") or ""
        self.view.toggle_name_display(new_state, name)

    def toggle_description_view(self):
        """トグル時は必ず現在の detail から desc を取り出して渡す"""
        new_state = not self.view.desc_is_visible
        desc = ""
        if getattr(self, "_current_detail", None):
            desc = self._current_detail.get('desc') or self._current_detail.get('explain') or ""
        else:
            try:
                if getattr(self.model, "current_word_id", None) and hasattr(self.model, "get_by_id"):
                    d = self.model.get_by_id(self.model.current_word_id) or {}
                    desc = d.get('desc') or d.get('explain') or ""
                elif hasattr(self.model, "get_current_detail"):
                    d = self.model.get_current_detail() or {}
                    desc = d.get('desc') or d.get('explain') or ""
            except Exception:
                desc = getattr(self.model, "wD", "") or ""
        self.view.toggle_description_display(new_state, desc)

    # --- データ切り替えロジック (次へ/前へ) ---
    def handle_next_word(self):
        if not hasattr(self.model, "go_to_next_word"):
            print("Warning: model has no go_to_next_word")
            return
        try:
            self.model.go_to_next_word()

            # 遷移後に最新の detail を取得して _set_current_detail を呼ぶ
            detail = None
            if hasattr(self.model, "get_by_id") and getattr(self.model, "current_word_id", None):
                try:
                    detail = self.model.get_by_id(self.model.current_word_id)
                except Exception:
                    detail = None

            if not detail and hasattr(self.model, "get_current_detail"):
                try:
                    detail = self.model.get_current_detail()
                except Exception:
                    detail = None

            if not detail:
                detail = {
                    'name': getattr(self.model, "wN", "") or "",
                    'desc': getattr(self.model, "wD", "") or "",
                    'tag': getattr(self.model, "wTag", None),
                    'category': getattr(self.model, "wCat", None)
                }
            self._set_current_detail(detail)
        except Exception as e:
            print(f"Error in handle_next_word: {e}")

    def handle_previous_word(self):
        if not hasattr(self.model, "go_to_previous_word"):
            print("Warning: model has no go_to_previous_word")
            return
        try:
            self.model.go_to_previous_word()

            detail = None
            if hasattr(self.model, "get_by_id") and getattr(self.model, "current_word_id", None):
                try:
                    detail = self.model.get_by_id(self.model.current_word_id)
                except Exception:
                    detail = None

            if not detail and hasattr(self.model, "get_current_detail"):
                try:
                    detail = self.model.get_current_detail()
                except Exception:
                    detail = None

            if not detail:
                detail = {
                    'name': getattr(self.model, "wN", "") or "",
                    'desc': getattr(self.model, "wD", "") or "",
                    'tag': getattr(self.model, "wTag", None),
                    'category': getattr(self.model, "wCat", None)
                }
            self._set_current_detail(detail)
        except Exception as e:
            print(f"Error in handle_previous_word: {e}")

    # --- 画面遷移プレースホルダー (Homeへ/一覧へ) ---
    def handle_go_home(self):
        self.root_controller.switch_view("home")

    def handle_go_word_list(self):
        self.root_controller.switch_view("wordlist")

    # --- 単語編集 ---
    def save_edits(self, name: str, description: str, tag: str, category: str):
        """
        View から送られた編集内容を Model.update_term に保存する。
        Model.update_term(question_id, word_name=..., explain=..., tag=..., category=...) -> bool
        """
        # current question_id を決定
        qid = None
        if getattr(self, "_current_detail", None):
            qid = self._current_detail.get('id') or self._current_detail.get('question_id') or None
        if not qid:
            qid = getattr(self.model, "current_word_id", None)

        # 正規化（Controller の方針: 空文字で明示的に上書き、Noneで変更しない）
        name = (name or "").strip()
        description = (description or "").strip()
        tag = (tag or "").strip()
        category = (category or "").strip()

        # qid が不明なら name から解決を試みる
        if not qid and name and hasattr(self.model, "get_term_detail"):
            d = self.model.get_term_detail(name)
            qid = d.get('id') if d else None

        try:
            if qid and hasattr(self.model, "update_term"):
                # Model.update_term の引数名に合わせて呼ぶ
                ok = self.model.update_term(
                    qid,
                    word_name=name or None,
                    explain=description or None,
                    tag=tag or None,
                    category=category or None
                )
                if not ok:
                    print("Warning: model.update_term returned False")
            else:
                print("Warning: No model.update_term or qid unknown; applying local reflect only")

            # 永続化の後、DBから最新レコードを取得して内部状態と view を最新化
            new_detail = None
            if qid and hasattr(self.model, "get_by_id"):
                new_detail = self.model.get_by_id(qid)
            if not new_detail and name and hasattr(self.model, "get_term_detail"):
                new_detail = self.model.get_term_detail(name)

            if new_detail:
                # model 側の保持（wN/wD/wTag/wCat/current_word_id）があれば更新しておく
                try:
                    if hasattr(self.model, "current_word_id"):
                        self.model.current_word_id = new_detail.get('id') or self.model.current_word_id
                    if hasattr(self.model, "wN"):
                        self.model.wN = new_detail.get('name') or new_detail.get('word_name') or ""
                    if hasattr(self.model, "wD"):
                        self.model.wD = new_detail.get('desc') or new_detail.get('explain') or ""
                    if hasattr(self.model, "wTag"):
                        self.model.wTag = new_detail.get('tag') or new_detail.get('tags') or None
                    if hasattr(self.model, "wCat"):
                        self.model.wCat = new_detail.get('category') or new_detail.get('cat') or None
                except Exception:
                    pass
                self._set_current_detail(new_detail)
            else:
                # DBから取れなければローカル反映
                self._set_current_detail({'id': qid, 'name': name, 'desc': description, 'tag': tag or None, 'category': category or None})

            # 編集モードを抜ける（View 側メソッド）
            try:
                self.view._exit_edit_widgets()
            except Exception:
                pass

        except Exception as e:
            print(f"Error saving edits: {e}")
            
    def cancel_edits(self):
        """編集キャンセル: current_detail を再反映して編集UIを閉じる"""
        try:
            if getattr(self, "_current_detail", None):
                self._set_current_detail(self._current_detail)
            else:
                qid = getattr(self.model, "current_word_id", None)
                if qid and hasattr(self.model, "get_by_id"):
                    d = self.model.get_by_id(qid)
                    if d:
                        self._set_current_detail(d)
            try:
                self.view._exit_edit_widgets()
            except Exception:
                pass
        except Exception as e:
            print(f"Error in cancel_edits: {e}")