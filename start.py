import os
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox

# =========================
# パス取得（exe / 通常両対応）
# =========================
def resource_path(relative_path: str) -> str:
    """
    リソースの絶対パスを取得する
    - exe 実行時 : exe のあるフォルダ基準
    - 通常実行  : start.py のあるフォルダ基準
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


# =========================
# 定数定義
# =========================
DB_PATH = resource_path("word_master.db")
VIEW_DIR = resource_path("view")
RESOURCE_DIR = resource_path("resources")


# =========================
# メイン処理
# =========================
def main():
    import traceback
    
    # デバッグ用：エラーログファイル作成
    log_file = resource_path("error.log")
    
    try:
        # --- DB存在チェック ---
        if not os.path.exists(DB_PATH):
            messagebox.showerror(
                "起動エラー",
                f"データベースが見つかりません。\n\n{DB_PATH}"
            )
            return

        # --- Tk 初期化 ---
        root = tk.Tk()
        root.title("IT Learning")

        # ここで Controller を生成する想定
        try:
            from Controller.AppController import AppController
        except Exception as e:
            messagebox.showerror(
                "起動エラー",
                f"Controller の読み込みに失敗しました。\n\n{e}"
            )
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Controller import error:\n{traceback.format_exc()}")
            return

        try:
            app = AppController(root, db_path=DB_PATH)
        except Exception as e:
            messagebox.showerror(
                "初期化エラー",
                f"AppController の初期化に失敗しました。\n\n{e}"
            )
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"AppController init error:\n{traceback.format_exc()}")
            return

        root.mainloop()
        
    except Exception as e:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Unexpected error:\n{traceback.format_exc()}")
        messagebox.showerror("エラー", f"予期しないエラーが発生しました。\n\n{e}")


# =========================
# エントリーポイント
# =========================
if __name__ == "__main__":
    main()
