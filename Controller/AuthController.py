# Controller/AuthController.py
from tkinter import messagebox
from View.AuthView import AuthView
from Model.SyncModel import SyncModel 

class AuthController:
    """認証画面のコントローラ"""
    
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = None
        self.reset_view = None

    def show(self):
        if self.reset_view: self.reset_view.hide()
        if self.view is None:
            self.view = AuthView(self.app.root, self)
        self.view.show()

    def hide(self):
        if self.view: self.view.hide()
        if self.reset_view: self.reset_view.hide()

    def login(self, login_id, password):
        """ログイン処理（サーバー認証優先）"""
        if not login_id or not password:
            messagebox.showwarning("入力エラー", "IDとパスワードを入力してください。")
            return

        # サーバーで直接認証
        sync_model = SyncModel(self.app.db_path)
        success, error_msg = sync_model.login(login_id, password)
        
        if success:
            messagebox.showinfo("成功", f"ようこそ、{login_id}さん！")
            
            # 同期画面へ遷移
            if hasattr(self.app, 'go_to_sync'):
                self.app.go_to_sync(login_id, password)
            else:
                self.app.switch_view("sync")
        else:
            messagebox.showerror("ログイン失敗", f"ログインに失敗しました:\n{error_msg}")

    def signup(self, login_id, password):
        """新規登録処理（サーバーのみ）"""
        if not login_id or not password:
            messagebox.showwarning("入力エラー", "IDとパスワードを入力してください。")
            return
            
        if len(password) < 4:
            messagebox.showwarning("入力エラー", "パスワードは4文字以上にしてください。")
            return

        # サーバーに直接登録
        sync_model = SyncModel(self.app.db_path)
        server_result = sync_model.register_user_to_server(login_id, password)
        
        if server_result['success']:
            messagebox.showinfo("成功", "登録が完了しました！")
            
            if hasattr(self.app, 'go_to_sync'):
                self.app.go_to_sync(login_id, password)
            else:
                self.app.switch_view("sync")
        else:
            messagebox.showerror("登録失敗", f"登録に失敗しました:\n{server_result.get('error')}")

    def go_to_home(self):
        self.app.switch_view("home")
    
    def go_to_reset(self):
        pass # 必要に応じて実装