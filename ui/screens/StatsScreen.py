import json, time
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QLabel, QScrollArea, QWidget, QSizePolicy
)
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import QTimer, Qt

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
        self.panel.setMinimumSize(500, 320)
        self.panel.setFixedWidth(620)

        self.title = PixelTextWidget(self.lang.get("game_stats"), TITLE_FONT_SIZE, MAIN_FONT, self.panel)
        self.title.set_effects(shadow=True)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""QScrollArea {background: transparent; border: none;}
        QScrollBar:vertical {background: #2a2a2a; width: 10px; border-radius: 5px;}
        QScrollBar::handle:vertical {background: #555; border-radius: 5px;min-height:20px}
        QScrollBar::handle:vertical:hover {background: #777;}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {height: 0px;}""")

        self.stats_container = QWidget()
        self.stats_container.setStyleSheet("background: transparent;")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(15, 10, 15, 10)
        self.stats_layout.setSpacing(10)
        self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.stats_container)

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

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_back)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()

        self.panel.addWidget(self.scroll_area)
        self.panel.main_layout.addSpacing(15)
        self.panel.main_layout.addLayout(btn_layout)
        self.panel.main_layout.addSpacing(15)

        self.menu_container = QWidget()
        menu_layout = QVBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(20)
        menu_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.panel, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(self.menu_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

        self.refresh_stats()
        self.update_ui()

    def back_to_menu(self):
        """
        Функция для возврата обратно в меню из настроек
        """
        self.game.sound_player.play("click")
        self.game.save_settings()
        if hasattr(self.game, 'stats_return_state') and self.game.stats_return_state:
            self.game.set_state(self.game.stats_return_state)
        else:
            self.game.set_state(States.MAIN_MENU)

    def refresh_stats(self):
        """
        Функция для обновления отображения списка статистики
        """
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                w = child.widget()
                w.setParent(None)
                w.deleteLater()

        self.stats_layout.invalidate()
        matches = self.game.stats_history.get_all_matches()
        if not matches:
            self.msg = PixelTextWidget(self.lang.get("no_matches_found"), 18, MAIN_FONT, self.stats_container)
            self.msg.set_effects(color=QColor(150, 150, 150), alignment=Qt.AlignmentFlag.AlignCenter)
            self.msg.setMinimumHeight(40) 
            self.stats_layout.addWidget(self.msg, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            self.msg = None
            for i, m in enumerate(matches, 1):
                text = f"{i}. {m['timestamp']} | WPM: {m['wpm']} | ACC: {m['accuracy']}%"
                row = PixelTextWidget(text, 16, MAIN_FONT, self.stats_container)
                row.set_effects(color=QColor(220, 220, 220), alignment=Qt.AlignmentFlag.AlignLeft)
                row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                row.setFixedHeight(36)
                self.stats_layout.addWidget(row)
        self.stats_layout.activate()
        QTimer.singleShot(0, self.adjust_panel_size)

    def reset_stats(self):
        self.game.sound_player.play("click")
        self.game.stats_history.matches = []
        self.game.stats_history.save()
        self.refresh_stats()

    def adjust_panel_size(self):
        if not hasattr(self, 'game') or not hasattr(self.game, 'stats_history'):
            return

        matches = self.game.stats_history.get_all_matches()
        
        if not matches:
            content_height = 40
        else:
            content_height = len(matches) * 36 + (len(matches) - 1) * 10 + 20

        chrome_height = 150 
        
        max_allowed_height = 520
        if self.height() > 100:
            max_allowed_height = min(520, self.height() - 60)

        final_height = max(320, min(content_height + chrome_height, max_allowed_height))

        self.panel.setFixedSize(620, final_height)
        self.scroll_area.verticalScrollBar().setValue(0)

        self.panel.updateGeometry()
        if hasattr(self, 'menu_container'):
            self.menu_container.updateGeometry()
            self.menu_container.adjustSize()
            
        if self.layout():
            self.layout().invalidate()
            self.layout().activate()
        self.update()
    
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

        self.refresh_stats()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 170))
        finally:
            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.adjust_panel_size)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_stats()