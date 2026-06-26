from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QColor,QPainter
from PySide6.QtCore import Qt

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class PauseScreen(BackgroundPage):
    """
    Класс меню паузы во время игры
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.game = obj
        self.lang = self.game.lang_manager

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.panel = MenuPlatform()

        self.title = PixelTextWidget(self.lang.get("title_pause"), TITLE_FONT_SIZE, MAIN_FONT, self.panel)
        self.title.set_effects(shadow=True)

        self.btn_resume = PixelButton(self.lang.get("btn_resume"), self.panel)
        self.btn_restart = PixelButton(self.lang.get("btn_restart"), self.panel)
        self.btn_statics = PixelButton(self.lang.get("btn_stats"), self.panel)
        self.btn_settings = PixelButton(self.lang.get("btn_settings"), self.panel)
        self.btn_menu = PixelButton(self.lang.get("btn_main_menu"), self.panel)
    
        self.btn_resume.clicked.connect(self.resume_game)
        self.btn_restart.clicked.connect(self.restart_game)
        self.btn_statics.clicked.connect(self.open_stats)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_menu.clicked.connect(self.back_to_menu)
        self.lang.language_changed.connect(self.update_ui)
        self.update_ui()

        self.panel.addWidget(self.btn_resume)
        self.panel.addWidget(self.btn_restart)
        self.panel.addWidget(self.btn_statics)
        self.panel.addWidget(self.btn_settings)
        self.panel.addWidget(self.btn_menu)

        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(20)
        menu_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.panel, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(menu_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
    
    def resume_game(self):
        self.game.sound_player.play("click")
        self.game.set_state(States.PLAYING)

    def restart_game(self):
        self.game.sound_player.play("click")
        self.game.restart_game()

    def open_settings(self):
        """
        Функция для открытия настроек во время паузы
        """
        self.game.sound_player.play("click")
        self.game.settings_pause_overlay = True
        self.game.set_state(States.SETTINGS)
    
    def open_stats(self):
        """
        Функция для открытия статистики во время паузы
        """
        self.game.sound_player.play("click")
        self.game.stats_overlay = True
        self.game.set_state(States.STATS)

    def back_to_menu(self):
        """
        Функция для возврата обратно в главное меню
        """
        self.game.sound_player.play("click")
        self.game.set_state(States.MAIN_MENU)

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """
        self.btn_resume.setText(self.lang.get("btn_resume"))
        self.btn_restart.setText(self.lang.get("btn_restart"))
        self.btn_statics.setText(self.lang.get("btn_stats"))
        self.btn_settings.setText(self.lang.get("btn_settings"))
        self.btn_menu.setText(self.lang.get("btn_main_menu"))
        self.title.setText(self.lang.get("title_pause"))

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 170))
        finally:
            painter.end()