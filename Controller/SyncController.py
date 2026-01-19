from Model.SyncModel import SyncModel
from View.SyncView import SyncView
import threading
import tkinter as tk

class SyncController:
    """同期画面コントローラ"""

    def __init__(self, app_controller, model: SyncModel = None):
        self.app = app_controller
        self.model = model if model else SyncModel()
        self.view = None
        self._last_user = None
        self._last_pass = None
        
        # データのキャッシュ
        self.local_terms = []
        self.server_terms = []

    def show(self):
        if self.view is None:
            self.view = SyncView(self.app.root, self)
            self.view.switch_mode("upload")
            if self.model.token:
                self.view.update_status(True, "接続済み")
        
        self.view.show()
        if self.view.mode == "upload":
            self.load_local_data()

    def hide(self):
        if self.view:
            self.view.hide()

    def go_to_home(self):
        self.app.switch_view("home")

    def setup_with_credentials(self, username, password):
        if self.view is None:
            self.show()
        self._last_user = username
        self._last_pass = password
        self.perform_login(username, password)

    # --- データ読み込み ---
    def load_local_data(self):
        """ローカルDBから単語リストを取得"""
        try:
            with self.model.get_conn() as conn:
                cur = conn.execute("SELECT * FROM terms WHERE is_deleted = 0")
                rows = cur.fetchall()
                self.local_terms = [dict(row) for row in rows]
            
            if self.view:
                self.view.update_term_list(self.local_terms)
        except Exception as e:
            print(f"Local data load error: {e}")
            if self.view:
                self.view.update_term_list([])

    def load_server_data(self):
        """サーバーから単語リストを取得して表示"""
        if not self.model.token:
            if self.view:
                self.view.update_term_list([])
                self.view.update_status(False, "未接続 - リストを取得するにはログインしてください")
            return

        def _fetch():
            if self.view:
                self.view.update_status(True, "サーバーデータ取得中...")
            
            # ▼▼▼ 修正: Modelからサーバーデータを取得 ▼▼▼
            result = self.model.fetch_server_terms()
            
            if 'error' in result:
                self.server_terms = []
                # エラーメッセージ表示などの処理
                print(f"Server fetch error: {result['error']}")
            else:
                self.server_terms = result.get('terms', [])

            if self.view:
                self.view.after(0, lambda: self.view.update_term_list(self.server_terms))
                self.view.after(0, lambda: self.view.update_status(True, "接続済み"))

        threading.Thread(target=_fetch, daemon=True).start()

    # --- フィルタ用 ---
    def get_categories(self):
        terms = self.local_terms if getattr(self.view, 'mode', 'upload') == 'upload' else self.server_terms
        cats = set(t.get('category') for t in terms if t.get('category'))
        return sorted(list(cats))

    def get_tags(self):
        terms = self.local_terms if getattr(self.view, 'mode', 'upload') == 'upload' else self.server_terms
        tags = set(t.get('tag') for t in terms if t.get('tag'))
        return sorted(list(tags))

    # --- アクションハンドラ ---
    def handle_upload_request(self, selected_uuids):
        if self.model.token:
            self._confirm_and_upload(selected_uuids)
        elif self._last_user and self._last_pass:
            self.perform_login(self._last_user, self._last_pass, 
                               next_action=lambda: self._confirm_and_upload(selected_uuids))
        else:
            self.view.show_login_dialog(
                lambda u, p: self._on_dialog_login(u, p, lambda: self._confirm_and_upload(selected_uuids))
            )

    def handle_download_request(self, selected_uuids):
        if self.model.token:
            self._confirm_and_download(selected_uuids)
        else:
            self.view.show_login_dialog(
                lambda u, p: self._on_dialog_login(u, p, lambda: self._confirm_and_download(selected_uuids))
            )

    def _on_dialog_login(self, user, pwd, next_action):
        self._last_user, self._last_pass = user, pwd
        self.perform_login(user, pwd, next_action)

    def perform_login(self, username, password, next_action=None):
        if self.view:
            self.view.update_status(False, "接続中...")
        def _task():
            success = self.model.login(username, password)
            if self.view:
                self.view.after(0, lambda: self._on_login_result(success, next_action))
        threading.Thread(target=_task, daemon=True).start()

    def _on_login_result(self, success, next_action):
        if success:
            if self.view: self.view.update_status(True, "接続成功")
            # ログイン成功時、現在がダウンロード画面ならリストを更新
            if self.view and self.view.mode == "download":
                self.load_server_data()
            if next_action: next_action()
        else:
            if self.view:
                self.view.update_status(False, "接続失敗")
                self.view.show_message("エラー", "ログインに失敗しました", True)

    def _confirm_and_upload(self, selected_uuids):
        if tk.messagebox.askyesno("確認", f"{len(selected_uuids)}件のデータをアップロードしますか？", parent=self.view):
            threading.Thread(target=self.perform_upload, args=(selected_uuids,), daemon=True).start()

    def _confirm_and_download(self, selected_uuids):
        if tk.messagebox.askyesno("確認", f"{len(selected_uuids)}件のデータをダウンロード（取り込み）しますか？", parent=self.view):
            threading.Thread(target=self.perform_download, args=(selected_uuids,), daemon=True).start()

    def perform_upload(self, selected_uuids):
        result = self.model.upload_data(target_uuids=selected_uuids)
        if self.view:
            self.view.after(0, lambda: self._on_sync_result(result, "アップロード"))

    def perform_download(self, selected_uuids):
        # ▼▼▼ 修正: 選択されたUUIDのデータだけを抽出して保存 ▼▼▼
        # サーバーデータキャッシュ(self.server_terms)から選択されたものを探す
        targets = [t for t in self.server_terms if t['uuid'] in selected_uuids]
        
        if not targets:
            if self.view: self.view.after(0, lambda: self.view.show_message("情報", "データが見つかりませんでした"))
            return

        result = self.model.import_to_local(targets)
        if self.view:
            self.view.after(0, lambda: self._on_sync_result(result, "ダウンロード"))

    def _on_sync_result(self, result, sync_type):
        if 'error' in result:
            self.view.show_message("エラー", result['error'], True)
        else:
            msg = f"{sync_type}完了\n新規: {result.get('new')} / 更新: {result.get('updated')}"
            self.view.show_message("成功", msg)
            
            # ダウンロード後は「アップロード画面(ローカル一覧)」を更新する必要があるが
            # 現在の画面がダウンロード画面のままなら、そのままにしておくか、あるいはダウンロード済みの印をつけるなどが理想
            # ここではシンプルに、ローカルデータキャッシュを更新しておく
            # (次にアップロード画面を開いたときに反映される)
            pass