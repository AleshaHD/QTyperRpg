import time
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, QTimer

from Configuration import *
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import TextLineWidget, PixelTextWidget
from ui.components.Keyboard import VirtualKeyboard

class GameScreen(BackgroundPage):
    """
    Класс экрана игры
    """
    def __init__(self, obj):
        super().__init__(obj, False, use_random=True, bg_color=WHITE)
        self.game = obj
        self.stats = self.game.stats
        self.lang = self.game.lang_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stats_bar = QWidget()
        stats_layout = QHBoxLayout(stats_bar)
        stats_layout.setContentsMargins(20, 15, 20, 0)
        stats_layout.setSpacing(20)

        label_text_size = 10
        self.wpm_label = PixelTextWidget("WPM: 0.0", font_size=label_text_size, font_path=MAIN_FONT, parent=self)
        self.acc_label = PixelTextWidget(f"{self.lang.get('acc')}: 0.0%", font_size=label_text_size, font_path=MAIN_FONT, parent=self)
        self.progress_label = PixelTextWidget(f"{self.lang.get('progress')}: 0.0", font_size=label_text_size, font_path=MAIN_FONT, parent=self)
        self.timer_label = PixelTextWidget(f"{self.lang.get('timer')}: 00:00", font_size=label_text_size, font_path=MAIN_FONT, parent=self)

        self.lang.language_changed.connect(self.update_ui)
        self.update_ui()

        stats_layout.addWidget(self.wpm_label)
        stats_layout.addWidget(self.acc_label)
        stats_layout.addWidget(self.progress_label)
        stats_layout.addWidget(self.timer_label)
        stats_layout.addStretch()

        self.text_widget = TextLineWidget()
        self.keyboard = VirtualKeyboard(self)

        layout.addWidget(stats_bar)
        layout.addStretch()
        layout.addWidget(self.text_widget)
        layout.addStretch()
        layout.addSpacing(100)

        self.setLayout(layout)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_timer_display)

    def ensure_timer_running(self):
        if self.stats.start_time is not None and not self.stats.is_finished and not self.ui_timer.isActive():
            self.ui_timer.start()

    def start_session(self):
        """
        Функция для запуска текста и экрана игры
        """
        self.refresh_background() 
        if self.particles_enabled:
            self.reset_particles()
        random_text = self.game.file.get_random_text(self.game.current_difficulty)
        self.stats.reset(random_text)
        self.update_text_display()
        self.update_stats_display()
        self.timer_label.setText(f"{self.lang.get('timer')}: 00:00")

    def update_text_display(self):
        """
        Функция для обновления текста на экране
        """
        self.text_widget.set_text_state(self.stats.target_text, self.stats.current_text_index)

        if self.stats.current_text_index < len(self.stats.target_text):
            next_char = self.stats.target_text[self.stats.current_text_index]
            self.keyboard.highlight_next_char(next_char)
        else:
            self.keyboard.clear_highlight()

    def update_stats_display(self):
        """
        Функция для обновления статистик на экране
        """
        self.wpm_label.setText(f"WPM: {self.stats.get_wpm()}")
        self.acc_label.setText(f"{self.lang.get('acc')}: {self.stats.get_accuracy()}%")
        self.progress_label.setText(f"{self.lang.get('progress')}: {self.stats.get_progress_bar()}%")

    def update_timer_display(self):
        """
        Функция для расчета прошедшего времени и обновления таймера
        """
        self.timer_label.setText(f"{self.lang.get('timer')}: {self.stats.get_timer()}")

    def handle_key(self, event: QKeyEvent):
        """
        Функция для получения вводимого текста пользователем
        """
        if event.key() == Qt.Key.Key_Escape:
            self.ui_timer.stop()
            self.game.set_state(States.PAUSE_MENU)
            return

        if event.key() == Qt.Key.Key_Space:
            char = ' '
        else:
            char = event.text()
            if not char:
                return

        if self.stats.current_text_index >= len(self.stats.target_text):
            return
        if not char:
            return

        expected_char = self.stats.target_text[self.stats.current_text_index]
        self.stats.total_attemts += 1

        if char == expected_char:
            if self.stats.start_time is None:
                self.stats.start_time = time.time()
                self.ensure_timer_running()

            self.stats.current_text_index += 1
            self.stats.hits.append(1)

            self.update_text_display()
            self.update_stats_display()

            if self.stats.current_text_index >= len(self.stats.target_text):
                self.ui_timer.stop()
                self.stats.finish_timer()
                QTimer.singleShot(0, self.game.finish_level)
                return
        else:
            self.stats.wrong_attemts += 1
            self.stats.hits.append(0)
            #print(f"WRONG \"{char}\" must \"{expected_char}\"")

        if len(self.stats.hits) > 127:
            self.stats.hits.pop(0)

        self.update_text_display()
        self.update_stats_display()

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """
        self.update_stats_display()
        self.update_timer_display()
        if self.isVisible(): 
            self.start_session()
        self.ensure_timer_running()

    def showEvent(self, event):
        super().showEvent(event)
        self.ensure_timer_running()
        self.update_timer_display()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        win_w = self.width()
        win_h = self.height()

        kb_width = int(win_w * 0.7)
        kb_width = min(max(kb_width, 600), 800)

        kb_height = int(win_h * 0.25)
        kb_height = min(max(kb_height, 200), 600)

        kb_x = (win_w - kb_width) // 2
        kb_y = win_h - kb_height - 50

        self.keyboard.setGeometry(kb_x, kb_y, kb_width, kb_height)

        visible = win_w >= 1100
        self.keyboard.left_hand_label.setVisible(visible)
        self.keyboard.right_hand_label.setVisible(visible)

        if visible:
            self.keyboard.resize_hands()

    def hideEvent(self, event):
        self.ui_timer.stop()
        super().hideEvent(event)