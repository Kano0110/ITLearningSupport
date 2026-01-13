#Q_quiz_view.py

import tkinter as tk
from tkinter import ttk

class Q_Quiz_View(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.pack(fill='both', expand=True)

        # 全体のレイアウト設定
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) # 中央（問題文）を広げる

        # === 上部エリア ===
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        top_frame.columnconfigure(1, weight=1)

        # 経過時間（左上）
        self.timer_label = ttk.Label(top_frame, text="経過時間: 00:00", font=("TkDefaultFont", 10))
        self.timer_label.grid(row=0, column=0, sticky="w")

        # タイトル（中央）
        self.question_label = ttk.Label(top_frame, text="", font=("TkDefaultFont", 12, "bold"))
        self.question_label.grid(row=0, column=1, sticky="n")

        # タグ・カテゴリ（右上）
        self.meta_label = ttk.Label(top_frame, text="", font=("TkDefaultFont", 9), foreground="gray")
        self.meta_label.grid(row=0, column=2, sticky="e")

        # === 問題表示エリア ===
        self.center_frame = ttk.Frame(self)
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        self.center_frame.columnconfigure(0, weight=1)

        # 問題文
        # 修正: wraplengthの固定値を削除し、動的に調整する
        self.display_area = ttk.Label(
            self.center_frame, 
            text="", 
            font=("TkDefaultFont", 16, "bold"), 
            anchor="center", 
            justify="center"
        )
        self.display_area.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # 修正: ウィンドウリサイズに合わせて折り返し幅を自動調整
        self.display_area.bind('<Configure>', self._on_label_configure)

        # 隠された部分（正解ワードなど）
        self.hidden_area = ttk.Label(self.center_frame, text="？？？", font=("TkDefaultFont", 14, "bold"), foreground="blue")
        self.hidden_area.grid(row=1, column=0, pady=(0, 20))

        # === 選択肢エリア ===
        self.choice_frame = ttk.Frame(self.center_frame)
        self.choice_frame.grid(row=2, column=0, pady=10)
        # 選択肢ボタンへの参照を保持するリスト
        self.choice_buttons = []

        # === 結果・操作エリア ===
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(2, weight=1)

        # 結果メッセージ
        self.result_label = ttk.Label(bottom_frame, text="", font=("TkDefaultFont", 14, "bold"))
        self.result_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # ボタン配置（左右対称にするためグリッドを使用）
        self.finish_btn = ttk.Button(bottom_frame, text="回答を終了する", command=self.controller.finish_quiz, width=15)
        self.finish_btn.grid(row=1, column=0, sticky="w") # 左寄せ

        self.next_btn = ttk.Button(bottom_frame, text="次の問題へ", command=self.controller.next_question, width=15)
        self.next_btn.grid(row=1, column=2, sticky="e") # 右寄せ

    def _on_label_configure(self, event):
        """ラベルのサイズ変更イベントで折り返し幅を更新"""
        # 現在の幅に合わせて折り返し設定 (少し余裕を持たせて -10)
        self.display_area.configure(wraplength=event.width - 10)

    def show(self):
        self.pack(fill='both', expand=True)

    def hide(self):
        self.pack_forget()

    def update_timer(self, elapsed_seconds):
        """経過時間を更新"""
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        self.timer_label.config(text=f"経過時間: {minutes:02}:{seconds:02}")

    def display_question(self, index, total, term, choices, mode, tag=None, category=None):
        self.clear_ui()
        self.question_label.config(text=f"第 {index} 問  /  全 {total} 問")

        meta_parts = []
        if category: meta_parts.append(f"カテゴリ: {category}")
        if tag: meta_parts.append(f"タグ: {tag}")
        self.meta_label.config(text="  ".join(meta_parts))

        if mode == "hide_word":
            self.display_area.config(text=term.get("desc", ""))
            self.hidden_area.config(text="？？？")
        elif mode == "hide_explanation":
            self.display_area.config(text=term.get("name", ""))
            self.hidden_area.config(text="？？？")
        else:
            self.display_area.config(text="（不明な出題形式）")

        # 選択肢ボタンの生成
        self.choice_buttons = [] # リセット
        labels = ["ア", "イ", "ウ", "エ"]
        
        # 選択肢フレーム内のクリア
        for child in self.choice_frame.winfo_children():
            child.destroy()

        for i, choice in enumerate(choices):
            full_text = choice.get("name") if mode == "hide_word" else choice.get("desc")
            
            # --- 修正: テキストが長すぎる場合は省略し、ツールチップを設定する ---
            display_text = full_text
            # 全角で概ね30文字程度、半角で60文字程度を目安にカット（環境依存ですが安全策として）
            # width=60 なので、それより少し少なめに設定しておくと改行されにくい
            if len(display_text) > 40:
                display_text = display_text[:38] + "..."
            
            # lambdaで変数をキャプチャする際、即時評価させる
            btn = ttk.Button(self.choice_frame, text=f"{labels[i]}. {display_text}", width=60,
                            command=lambda c=choice: self.controller.handle_answer(c))
            btn.pack(anchor='center', pady=5, ipadx=5, ipady=2)
            
            # ツールチップを設定 (省略されていない場合でも全文表示用に設定しても良い)
            create_tooltip(btn, full_text)
            
            # ボタンオブジェクトと紐づくデータを保持しておく（結果表示用）
            btn.choice_data = choice 
            # 全文も保持しておき、結果表示時に使うなどの拡張も可能
            btn.full_text = full_text
            self.choice_buttons.append(btn)

    def show_result(self, is_correct, correct_term, selected_choice):
        """回答後の正誤表示と選択肢の状態更新"""
        self.result_label.config(
            text="正解！" if is_correct else "残念… 不正解です",
            foreground="green" if is_correct else "red"
        )

        # 隠されていた部分を表示
        if self.controller.mode == "hide_word":
            self.hidden_area.config(text=correct_term.get("name", ""))
        else:
            self.hidden_area.config(text=correct_term.get("desc", ""))

        # 選択肢ボタンの状態更新
        for btn in self.choice_buttons:
            btn.state(['disabled']) # 全ボタン無効化
            
            choice_id = btn.choice_data.get("id")
            correct_id = correct_term.get("id")
            selected_id = selected_choice.get("id")

            # テキストの装飾
            # 省略前のテキストを使うかどうかは好みですが、
            # 結果表示時もボタンサイズを変えないために省略テキストのままマークを付ける
            original_text = btn.cget("text")
            
            if choice_id == correct_id:
                # 正解の選択肢
                btn.config(text=f"★正解★ {original_text}")
            
            if choice_id == selected_id and not is_correct:
                # 自分が選んだ間違った選択肢
                btn.config(text=f"✖あなたの回答 {original_text}")

        # 次へ／終了ボタンを表示
        self.next_btn.grid()
        self.finish_btn.grid()

    def clear_ui(self):
        """前問のUIを初期化"""
        self.result_label.config(text="")
        self.hidden_area.config(text="？？？")
        # ボタンを隠す
        self.next_btn.grid_remove()
        self.finish_btn.grid_remove()

# --- ツールチップ用クラス ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None

    def show(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        # ウィンドウの装飾をなくす
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"), wraplength=400) # ツールチップ内でも折り返す
        label.pack(ipadx=1)

    def hide(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    tool_tip = ToolTip(widget, text)
    def enter(event):
        tool_tip.show()
    def leave(event):
        tool_tip.hide()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)