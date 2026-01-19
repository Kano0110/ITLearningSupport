# Controller/AuthController.py
from tkinter import messagebox
from Model.AuthModel import AuthModel
from View.AuthView import AuthView
# SyncModelが必要なのでインポート
from Model.SyncModel import SyncModel 

class AuthController:
    """認証画面のコントローラ"""
    
    def __init__(self, app_controller, model: AuthModel = None):
        self.app = app_controller
        self.model = model if model else AuthModel()
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
        """ログイン処理（サーバー自動登録機能付き）"""
        if not login_id or not password:
            messagebox.showwarning("入力エラー", "IDとパスワードを入力してください。")
            return

        # 1. ローカルDB (SQLite) でログイン確認
        if self.model.login_user(login_id, password):
            
            # 2. サーバー接続確認 (自己修復ロジック)
            # ローカルOKなら、サーバーにもそのユーザーがいるか確認する
            sync_model = SyncModel(self.app.db_path)
            if not sync_model.login(login_id, password):
                print(f"DEBUG: サーバーログイン失敗。未登録の可能性があるため、サーバーへの自動登録を試みます: {login_id}")
                
                # サーバーに登録を試みる
                reg_result = sync_model.register_user_to_server(login_id, password)
                if reg_result['success']:
                    print("DEBUG: サーバーへの自動登録成功")
                else:
                    print(f"DEBUG: サーバーへの自動登録失敗: {reg_result.get('error')}")
                    # ここで失敗しても、とりあえずローカルログインは成功しているので進ませる
            
            messagebox.showinfo("成功", f"ようこそ、{login_id}さん！")
            
            # 3. 同期画面へ遷移
            if hasattr(self.app, 'go_to_sync'):
                self.app.go_to_sync(login_id, password)
            else:
                self.app.switch_view("sync")
                
        else:
            messagebox.showerror("エラー", "IDまたはパスワードが間違っています。")

    def signup(self, login_id, password):
        """新規登録処理"""
        if not login_id or not password:
            messagebox.showwarning("入力エラー", "IDとパスワードを入力してください。")
            return
            
        if len(password) < 4:
            messagebox.showwarning("入力エラー", "パスワードは4文字以上にしてください。")
            return

        # 1. ローカルDB登録
        if self.model.register_user(login_id, password):
            
            # 2. サーバーDB登録
            sync_model = SyncModel(self.app.db_path)
            server_result = sync_model.register_user_to_server(login_id, password)
            
            msg = "登録が完了しました！"
            if not server_result['success']:
                msg += f"\n(サーバー登録のみ失敗: {server_result.get('error')})"
            
            messagebox.showinfo("成功", msg)
            
            if hasattr(self.app, 'go_to_sync'):
                self.app.go_to_sync(login_id, password)
            else:
                self.app.switch_view("sync")
        else:
            messagebox.showerror("エラー", "このIDは既に使用されています。")

    def go_to_home(self):
        self.app.switch_view("home")
    
    def go_to_reset(self):
        pass # 必要に応じて実装