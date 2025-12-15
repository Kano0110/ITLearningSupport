# HomeView.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class HomeView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("HOME")
        self.controller = controller  # MainControllerへの参照
        self.bg_image = None  # 背景画像の参照を保持

        self._create_widgets()
        self.pack(expand=True, fill='both')

    def _create_widgets(self):
        # 背景画像の設定
        self._set_background()
        
        # ラベル
        label = ttk.Label(self, text="HOME", font=('Arial', 24))
        label.pack(padx=20, pady=40)

        # 単語一覧ボタン（上から1番目）
        wordlist_button = ttk.Button(self, text="単語一覧",
                                command=self.controller.go_to_wordlist)
        wordlist_button.pack(pady=10, ipadx=20)

        # 問題を解くボタン（上から2番目）
        quiz_button = ttk.Button(self, text="問題を解く",
                                command=self.controller.go_to_quiz)
        quiz_button.pack(pady=10, ipadx=20)
    
    def _set_background(self):
        """背景画像を設定"""
        try:
            # 画像ファイルのパスを探す（複数の可能性を試す）
            possible_paths = [
                'green-sky.jpg',
                os.path.join('resources', 'green-sky.jpg'),
            ]
            
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if image_path:
                # 画像を読み込み
                image = Image.open(image_path)
                # ウィンドウサイズに合わせてリサイズ（必要に応じて調整）
                image = image.resize((800, 600), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(image)
                
                # 背景ラベルを作成
                bg_label = tk.Label(self, image=self.bg_image)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                bg_label.lower()  # 他のウィジェットの後ろに配置
            else:
                # 画像が見つからない場合は背景色を設定
                self.configure(bg='#E8F4F8')
        except Exception as e:
            print(f"背景画像の読み込みに失敗しました: {e}")
            # エラー時は背景色を設定
            self.configure(bg='#E8F4F8')