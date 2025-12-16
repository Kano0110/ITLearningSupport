# HomeView.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class HomeView(tk.Frame):
    """HOME画面ビュー（背景画像表示・ボタン配置）"""
    
    # 定数
    RESIZE_DEBOUNCE_MS = 50
    MIN_FALLBACK_WIDTH = 800
    MIN_FALLBACK_HEIGHT = 600
    MIN_SIZE_THRESHOLD = 10
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
    BG_IMAGE_NAMES = ['green-sky.jpg', os.path.join('resources', 'green-sky.jpg')]
    FALLBACK_BG_COLOR = '#E8F4F8'
    ERROR_BG_COLOR = '#47BFFB'
    
    def __init__(self, master, controller):
        super().__init__(master)
        self.master.title("HOME")
        self.controller = controller
        
        # 背景画像管理
        self.bg_image = None
        self._bg_original = None
        self._bg_label = None
        self._bg_cache_size = None  # キャッシュされた画像のサイズ (w, h)
        
        # リサイズイベント管理
        self._resize_after_id = None

        self._create_widgets()
        self.pack(expand=True, fill='both')

    def _create_widgets(self):
        """UI要素を構築"""
        self._load_and_set_background()
        self._create_title_label()
        self._create_navigation_buttons()
    
    def _create_title_label(self):
        """タイトルラベルを作成"""
        label = ttk.Label(self, text="HOME", font=('Arial', 28, 'bold'))
        label.pack(padx=24, pady=48)
    
    def _create_navigation_buttons(self):
        """ナビゲーションボタンを作成"""
        wordlist_button = ttk.Button(
            self, 
            text="単語一覧",
            command=self.controller.go_to_wordlist
        )
        wordlist_button.pack(pady=12, ipadx=26, ipady=6)

        quiz_button = ttk.Button(
            self, 
            text="問題を解く",
            command=self.controller.go_to_quiz
        )
        quiz_button.pack(pady=12, ipadx=26, ipady=6)
    
    def _load_and_set_background(self):
        """背景画像を読み込んで設定"""
        try:
            image_path = self._find_background_image()
            if image_path:
                self._load_background_image(image_path)
            else:
                self._set_fallback_bg_color()
        except Exception as e:
            print(f"背景画像の読み込みに失敗しました: {e}")
            self._set_error_bg_color()
    
    def _find_background_image(self) -> str | None:
        """背景画像ファイルを探索"""
        for path in self.BG_IMAGE_NAMES:
            if os.path.exists(path):
                return path
        return None
    
    def _load_background_image(self, image_path: str):
        """背景画像をロードして初期表示"""
        self._bg_original = Image.open(image_path)
        self._update_background_image()
        
        if self._bg_label is None:
            self._bg_label = tk.Label(self, image=self.bg_image)
            self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self._bg_label.lower()
        else:
            self._bg_label.configure(image=self.bg_image)
        
        # リサイズイベント登録
        self.bind('<Configure>', self._on_resize)
    
    def _set_fallback_bg_color(self):
        """フォールバック背景色を設定"""
        self.configure(bg=self.FALLBACK_BG_COLOR)
    
    def _set_error_bg_color(self):
        """エラー時の背景色を設定"""
        self.configure(bg=self.ERROR_BG_COLOR)

    def _on_resize(self, event):
        """フレームリサイズ時に背景画像をデバウンス更新"""
        if event.width <= 1 or event.height <= 1:
            return
        
        # 直前の予約更新があればキャンセル
        self._cancel_pending_resize()
        
        def _do_update():
            self._resize_after_id = None
            self._update_background_image(event.width, event.height)
            if self._bg_label is not None and self.bg_image is not None:
                self._bg_label.configure(image=self.bg_image)
        
        self._resize_after_id = self.after(self.RESIZE_DEBOUNCE_MS, _do_update)
    
    def _cancel_pending_resize(self):
        """保留中のリサイズ処理をキャンセル"""
        if self._resize_after_id is not None:
            try:
                self.after_cancel(self._resize_after_id)
            except Exception:
                pass
            self._resize_after_id = None

    def destroy(self):
        """破棄時にリソースクリーンアップ"""
        self._cancel_pending_resize()
        self._unbind_resize_event()
        self._cleanup_bg_image()
        super().destroy()
    
    def _unbind_resize_event(self):
        """リサイズイベントのバインドを解除"""
        try:
            self.unbind('<Configure>')
        except Exception:
            pass
    
    def _cleanup_bg_image(self):
        """背景画像リソースをクリーンアップ"""
        self._bg_original = None
        self._bg_image = None
        self._bg_cache_size = None

    def _update_background_image(self, w: int | None = None, h: int | None = None):
        """背景画像を現在のウィンドウサイズに合わせてリサイズ・更新"""
        if self._bg_original is None:
            return
        
        # 表示サイズを決定
        target_w, target_h = self._get_target_size(w, h)
        
        # キャッシュチェック（同サイズなら再生成をスキップ）
        if self._is_image_cached(target_w, target_h):
            return
        
        # 画像をリサイズして更新
        self._resize_and_apply_image(target_w, target_h)
    
    def _get_target_size(self, w: int | None, h: int | None) -> tuple[int, int]:
        """表示対象サイズを決定"""
        if w is None or h is None:
            try:
                self.update_idletasks()
            except Exception:
                pass
            w = max(self.winfo_width(), 1)
            h = max(self.winfo_height(), 1)
        
        # フォールバック：初期化直後のサイズ0を回避
        if w < self.MIN_SIZE_THRESHOLD or h < self.MIN_SIZE_THRESHOLD:
            w = max(self.master.winfo_width(), self.MIN_FALLBACK_WIDTH)
            h = max(self.master.winfo_height(), self.MIN_FALLBACK_HEIGHT)
        
        return int(w), int(h)
    
    def _is_image_cached(self, w: int, h: int) -> bool:
        """キャッシュされた画像が同サイズであるかチェック"""
        return self._bg_cache_size == (w, h)
    
    def _resize_and_apply_image(self, w: int, h: int):
        """画像をリサイズしてラベルに適用"""
        try:
            img = self._bg_original.copy()
            img = img.resize((w, h), self.RESAMPLE_FILTER)
            self.bg_image = ImageTk.PhotoImage(img)
            self._bg_cache_size = (w, h)
        except Exception as e:
            print(f"背景画像のリサイズに失敗: {e}")