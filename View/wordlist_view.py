import sys
import os

# プロジェクトのルートディレクトリをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

"""
View層: UIの表示とユーザー操作の受付
MVCパターンに対応したIT用語辞書のメインアプリケーション
"""
import tkinter as tk
from tkinter import ttk, messagebox
from Controller.wordlist_controller import WordListController

MAX_ROWS_PER_COLUMN = 20  # 1列あたりの最大行数


class WordListView:
    """IT用語辞書のビュー（UI）"""
    
    def __init__(self, controller: WordListController):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("IT用語辞書")
        self.root.geometry("600x440")
        
        # UI要素の参照を保持
        self.search_var = None
        self.scrollable_frame = None
        self.canvas = None
        
        # UIを構築
        self._build_ui()
        
        # コントローラにコールバックを設定
        self.controller.set_view_update_callback(self.display_terms)
    
    def _build_ui(self):
        """UIコンポーネントを構築"""
        self._create_index_buttons()
        self._create_search_bar()
        self._create_list_area()
    
    def _create_index_buttons(self):
        """五十音索引ボタンを作成"""
        index_frame = ttk.Frame(self.root, padding=8)
        index_frame.pack(fill='x')
        
        categories = self.controller.get_available_categories()
        
        for category in categories:
            btn = ttk.Button(
                index_frame,
                text=category,
                width=3,
                command=lambda c=category: self.on_category_click(c)
            )
            btn.pack(side='left', padx=2)
        
        # 「全て」ボタンを追加
        all_btn = ttk.Button(
            index_frame,
            text="全て",
            width=4,
            command=self.on_show_all_click
        )
        all_btn.pack(side='left', padx=2)
    
    def _create_search_bar(self):
        """検索バーを作成"""
        search_frame = ttk.Frame(self.root, padding=(8, 4))
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="絞り込み:").pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(6, 4))
        
        # 検索文字列の変更を監視
        self.search_var.trace_add('write', self.on_search_change)
        
        clear_btn = ttk.Button(
            search_frame,
            text="クリア",
            command=self.on_clear_search_click
        )
        clear_btn.pack(side='left')
        
        # 統計情報表示（オプション）
        stats = self.controller.get_stats()
        total = stats.get('total', 0)
        stats_label = ttk.Label(
            search_frame,
            text=f"総用語数: {total}",
            foreground='gray'
        )
        stats_label.pack(side='right', padx=10)
    
    def _create_list_area(self):
        """用語リスト表示エリアを作成"""
        list_frame = ttk.Frame(self.root, padding=8)
        list_frame.pack(expand=True, fill='both')
        
        # Canvas + Scrollbar でスクロール可能に
        self.canvas = tk.Canvas(list_frame)
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
    
    def display_terms(self, terms: list, message: str = None):
        """
        用語リストを表示
        
        Args:
            terms: 表示する用語のリスト
            message: 空の場合に表示するメッセージ
        """
        # 既存のウィジェットを削除
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if terms:
            # 用語を複数列で表示
            for i, name in enumerate(terms):
                row_index = i % MAX_ROWS_PER_COLUMN
                col_index = i // MAX_ROWS_PER_COLUMN
                
                # クリック可能なラベルとして表示
                lbl = ttk.Label(
                    self.scrollable_frame,
                    text=name,
                    padding=(4, 2),
                    cursor='hand2'
                )
                lbl.grid(row=row_index, column=col_index, sticky='w')
                
                # クリックイベントをバインド
                lbl.bind('<Button-1>', lambda e, term=name: self.on_term_click(term))
                
                # ホバー効果（オプション）
                lbl.bind('<Enter>', lambda e, l=lbl: l.configure(foreground='blue'))
                lbl.bind('<Leave>', lambda e, l=lbl: l.configure(foreground='black'))
        else:
            # 空の場合のメッセージ
            if message is None:
                message = "用語が見つかりません"
            
            ttk.Label(
                self.scrollable_frame,
                text=message,
                foreground='gray'
            ).grid(row=0, column=0, sticky='w')
        
        # スクロール領域を更新
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def on_category_click(self, category: str):
        """五十音ボタンがクリックされた時の処理"""
        self.controller.select_category(category)
    
    def on_show_all_click(self):
        """「全て」ボタンがクリックされた時の処理"""
        self.controller.clear_category()
    
    def on_search_change(self, *args):
        """検索欄の内容が変更された時の処理"""
        query = self.search_var.get()
        self.controller.apply_search(query)
    
    def on_clear_search_click(self):
        """検索クリアボタンがクリックされた時の処理"""
        self.search_var.set("")
        self.controller.clear_search()
    
    def on_term_click(self, term: str):
        """用語がクリックされた時の処理"""
        detail = self.controller.get_term_detail(term)
        if detail:
            # 詳細情報を表示（新しいウィンドウ）
            self._show_detail_window(detail)
        else:
            messagebox.showwarning("警告", f"'{term}'の詳細情報が見つかりません")
    
    def _show_detail_window(self, detail: dict):
        """詳細情報を別ウィンドウで表示"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"詳細 - {detail['word_name']}")
        detail_window.geometry("500x450")
        
        # メインフレーム
        main_frame = ttk.Frame(detail_window, padding=10)
        main_frame.pack(expand=True, fill='both')
        
        # スクロール可能なテキストウィジェット
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(expand=True, fill='both')
        
        text_widget = tk.Text(text_frame, wrap='word', padx=10, pady=10, font=('TkDefaultFont', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        # 詳細情報を挿入
        text_widget.insert('1.0', f"【用語名】\n{detail['word_name']}\n\n")
        
        if detail.get('yomi'):
            text_widget.insert('end', f"【読み】\n{detail['yomi']}\n\n")
        
        if detail.get('explain'):
            text_widget.insert('end', f"【説明】\n{detail['explain']}\n\n")
        
        if detail.get('tag'):
            text_widget.insert('end', f"【タグ】\n{detail['tag']}\n\n")
        
        if detail.get('category'):
            text_widget.insert('end', f"【カテゴリ】\n{detail['category']}\n")
        
        text_widget.config(state='disabled')  # 読み取り専用
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 編集ボタン
        edit_btn = ttk.Button(
            button_frame,
            text="編集",
            command=lambda: self._show_edit_window(detail, detail_window)
        )
        edit_btn.pack(side='left', padx=5)
        
        # 削除ボタン
        delete_btn = ttk.Button(
            button_frame,
            text="削除",
            command=lambda: self._confirm_delete(detail['word_name'], detail_window)
        )
        delete_btn.pack(side='left', padx=5)
        
        # 閉じるボタン
        close_btn = ttk.Button(
            button_frame,
            text="閉じる",
            command=detail_window.destroy
        )
        close_btn.pack(side='left', padx=5)
    
    def _show_edit_window(self, detail: dict, parent_window: tk.Toplevel):
        """編集ウィンドウを表示"""
        edit_window = tk.Toplevel(parent_window)
        edit_window.title(f"編集 - {detail['word_name']}")
        edit_window.geometry("450x400")
        
        main_frame = ttk.Frame(edit_window, padding=15)
        main_frame.pack(expand=True, fill='both')
        
        # 各フィールドのラベルと入力欄
        ttk.Label(main_frame, text="用語名:").grid(row=0, column=0, sticky='w', pady=5)
        word_name_var = tk.StringVar(value=detail['word_name'])
        ttk.Entry(main_frame, textvariable=word_name_var, width=40, state='readonly').grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="読み:").grid(row=1, column=0, sticky='w', pady=5)
        yomi_var = tk.StringVar(value=detail.get('yomi', ''))
        ttk.Entry(main_frame, textvariable=yomi_var, width=40).grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="説明:").grid(row=2, column=0, sticky='nw', pady=5)
        explain_text = tk.Text(main_frame, width=40, height=8, wrap='word')
        explain_text.insert('1.0', detail.get('explain', ''))
        explain_text.grid(row=2, column=1, pady=5)
        
        ttk.Label(main_frame, text="タグ:").grid(row=3, column=0, sticky='w', pady=5)
        tag_var = tk.StringVar(value=detail.get('tag', ''))
        ttk.Entry(main_frame, textvariable=tag_var, width=40).grid(row=3, column=1, pady=5)
        
        ttk.Label(main_frame, text="カテゴリ:").grid(row=4, column=0, sticky='w', pady=5)
        category_var = tk.StringVar(value=detail.get('category', ''))
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=37)
        category_combo['values'] = self.controller.get_available_categories()
        category_combo.grid(row=4, column=1, pady=5)
        
        # 保存・キャンセルボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        def save_changes():
            explain = explain_text.get('1.0', 'end-1c')
            success = self.controller.update_term(
                word_name=detail['word_name'],
                yomi=yomi_var.get() or None,
                explain=explain or None,
                tag=tag_var.get() or None,
                category=category_var.get() or None
            )
            if success:
                messagebox.showinfo("成功", "用語を更新しました", parent=edit_window)
                edit_window.destroy()
                parent_window.destroy()
            else:
                messagebox.showerror("エラー", "用語の更新に失敗しました", parent=edit_window)
        
        ttk.Button(button_frame, text="保存", command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="キャンセル", command=edit_window.destroy).pack(side='left', padx=5)
    
    def _confirm_delete(self, word_name: str, parent_window: tk.Toplevel):
        """削除確認ダイアログを表示"""
        result = messagebox.askyesno(
            "削除確認",
            f"'{word_name}'を削除しますか？\nこの操作は元に戻せません。",
            parent=parent_window
        )
        if result:
            success = self.controller.delete_term(word_name)
            if success:
                messagebox.showinfo("成功", "用語を削除しました", parent=parent_window)
                parent_window.destroy()
            else:
                messagebox.showerror("エラー", "用語の削除に失敗しました", parent=parent_window)
    
    def run(self):
        """アプリケーションを起動"""
        # 初期化
        if not self.controller.initialize():
            messagebox.showerror("エラー", "データベースが見つかりません")
        
        # メインループ開始
        self.root.mainloop()


def main():
    """メインエントリーポイント"""
    controller = WordListController()
    view = WordListView(controller)
    view.run()


if __name__ == "__main__":
    main()
