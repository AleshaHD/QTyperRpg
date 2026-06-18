from PySide6.QtWidgets import QVBoxLayout, QWidget

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class MainMenu(BackgroundPage):
    """
    Класс начального экрана
    """
    def __init__(self, obj):
        super().__init__(obj, True, bg_path=MAIN_MENU_BG)
        self.game = obj
        self.lang = self.game.lang_manager

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.title = PixelTextWidget("QTyper", TITLE_FONT_SIZE, MAIN_FONT, self)
        self.title.set_effects(shadow=True)

        self.panel = MenuPlatform()

        self.btn_start = PixelButton(self.lang.get("btn_start"), self.panel)
        self.btn_stats = PixelButton(self.lang.get("btn_stats"), self.panel)
        self.btn_settings = PixelButton(self.lang.get("btn_settings"), self.panel)
        self.btn_exit = PixelButton(self.lang.get("btn_exit"), self.panel)

        self.btn_start.clicked.connect(self.select_session)
        self.btn_stats.clicked.connect(self.open_stats)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_exit.clicked.connect(self.game.close)
        self.lang.language_changed.connect(self.update_ui)
        self.update_ui()

        self.panel.layout.addWidget(self.btn_start)
        self.panel.layout.addWidget(self.btn_stats)
        self.panel.layout.addWidget(self.btn_settings)
        self.panel.layout.addWidget(self.btn_exit)

        self.menu_container = QWidget()
        menu_layout = QVBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(20)
        menu_layout.addWidget(self.title)
        menu_layout.addWidget(self.panel)

        layout.addStretch()
        layout.addWidget(self.menu_container)
        layout.addStretch()

        self.setLayout(layout)

    def select_session(self):
        """
        Функция для выбора уровня
        """
        self.game.sound_player.play("click")
        self.game.set_state(States.SELECT_SESSION)

    def open_settings(self):
        """
        Функция для открытия настроек
        """
        self.game.sound_player.play("click")
        self.game.settings_pause_overlay = False
        self.game.set_state(States.SETTINGS)

    def open_stats(self):
        """
        Функция для открытия статистики
        """
        self.game.sound_player.play("click")
        self.game.stats_overlay = False
        self.game.set_state(States.STATS)

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """
        self.btn_start.setText(self.lang.get("btn_start"))
        self.btn_stats.setText(self.lang.get("btn_stats"))
        self.btn_settings.setText(self.lang.get("btn_settings"))
        self.btn_exit.setText(self.lang.get("btn_exit"))