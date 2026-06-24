import json, time
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QLabel, QScrollArea, QWidget, QSizePolicy
)
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class StatsHistory:
    """
    Класс для сохранения истории статистики
    """
    def __init__(self):
        self.matches = []
        self.load()

    def add_match(self, wpm, acc, timer):
        match_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),"wpm": wpm, "accuracy": acc, "timer": timer}
        self.matches.append(match_data)
        self.save()

    def load(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.matches = data.get("matches", [])
            except:
                self.matches = []

    def save(self):
        ensure_dir_exists(STATS_FILE)
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'matches': self.matches}, f, indent=4, ensure_ascii=False)

    def get_all_matches(self):
        return self.matches[::-1]

class StatsScreen(BackgroundPage):
    """
    Класс экрана статистики
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.game = obj
        self.lang = self.game.lang_manager
        self.msg = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.panel = MenuPlatform()
        self.panel.setMinimumHeight(320)

        self.title = PixelTextWidget(self.lang.get("game_stats"), TITLE_FONT_SIZE, MAIN_FONT, self.panel)
        self.title.set_effects(shadow=True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""QScrollArea {background: transparent; border: none;}
        QScrollBar:vertical {background: #2a2a2a; width: 10px; border-radius: 5px;}
        QScrollBar::handle:vertical {background: #555; border-radius: 5px;min-height:20px}
        QScrollBar::handle:vertical:hover {background: #777;}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {height: 0px;}""")

        self.stats_container = QWidget()
        self.stats_container.setStyleSheet("background: transparent;")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(5, 5, 5, 5)
        self.stats_layout.setSpacing(10)
        self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.stats_container)

        self.stats_text = QLabel()
        self.stats_text.setWordWrap(True)
        self.stats_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_text.setTextFormat(Qt.TextFormat.PlainText)
        self.stats_text.setStyleSheet("""
        QLabel {color: #d0d0d0; font-size: 20px;
        background: transparent; padding: 5px;}""")

        self.btn_back = PixelButton(self.lang.get("btn_back"), self.panel)
        self.btn_reset = PixelButton(self.lang.get("clear_stats"), self.panel)
        self.btn_back.clicked.connect(self.back_to_menu)
        self.btn_reset.clicked.connect(self.reset_stats)
        self.lang.language_changed.connect(self.update_ui)
        self.update_ui()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_back)
        btn_layout.addWidget(self.btn_reset)

        self.panel.layout.addWidget(scroll_area)
        self.panel.layout.addLayout(btn_layout)

        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(20)
        menu_layout.addWidget(self.title)
        menu_layout.addWidget(self.panel)

        layout.addStretch()
        layout.addWidget(menu_container)
        layout.addStretch()

        self.setLayout(layout)

        self.refresh_stats()

    def back_to_menu(self):
        """
        Функция для возврата обратно в меню из настроек
        """
        self.game.sound_player.play("click")
        self.game.save_settings()
        if hasattr(self.game, 'return_state') and self.game.return_state in (States.PAUSE_MENU, States.PLAYING, States.END_SCREEN):
            self.game.set_state(self.game.return_state)
        else:
            self.game.set_state(States.MAIN_MENU)

    def refresh_stats(self):
        """
        Функция для обновления отображения списка статистики
        """
        self.game.sound_player.play("click")
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        matches = self.game.stats_history.get_all_matches()
        if not matches:
            self.msg = PixelTextWidget(self.lang.get("no_matches_found"), 18, MAIN_FONT, self)
            self.msg.set_effects(color=QColor(150, 150, 150))
            self.stats_layout.addWidget(self.msg)
        else:
            for i, m in enumerate(matches, 1):
                text = f"{i}. {m['timestamp']} | WPM: {m['wpm']} | ACC: {m['accuracy']}%"
                row = PixelTextWidget(text, 16, MAIN_FONT, self)
                row.set_effects(color=QColor(220, 220, 220), alignment=Qt.AlignmentFlag.AlignLeft)
                row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                self.stats_layout.addWidget(row)
        self.stats_container.adjustSize()
        self.adjust_panel_size()

    def reset_stats(self):
        self.game.stats_history.matches = []
        self.game.stats_history.save()
        self.refresh_stats()
        self.msg = None

    def adjust_panel_size(self):
        self.stats_layout.activate()
        self.stats_container.adjustSize()

        stats_h = self.stats_container.sizeHint().height()
        title_h = self.title.sizeHint().height()
        buttons_h = self.btn_back.sizeHint().height() + 40 

        must_height = title_h + stats_h + buttons_h + 100
        max_height = self.height() - 100
        min_height = 320
        final_height = max(min_height, min(must_height, max_height))

        stats_w = self.stats_container.sizeHint().width()
        title_w = self.title.sizeHint().width()
        btns_w = self.btn_back.sizeHint().width() + self.btn_reset.sizeHint().width() + 60

        final_width = max(title_w, stats_w, btns_w, 300) + 80
        final_width = min(final_width, 700)

        self.panel.setMinimumSize(int(final_width), int(final_height))
        self.panel.resize(int(final_width), int(final_height))
        self.panel.update()

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """
        if self.msg is not None:
            self.msg.set_text(self.lang.get("no_matches_found"))
        self.btn_back.setText(self.lang.get("btn_back"))
        self.btn_reset.setText(self.lang.get("clear_stats"))
        self.title.setText(self.lang.get("game_stats"))

        self.title.adjustSize()
        self.btn_back.adjustSize()
        self.btn_reset.adjustSize()
        self.adjust_panel_size()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 170))
        finally:
            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)