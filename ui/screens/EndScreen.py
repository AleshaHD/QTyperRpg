from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class EndScreen(BackgroundPage):
    """
    Класс конечного экрана с подсчетом статистики
    """
    def __init__(self, obj):
        super().__init__(obj, True, bg_path=MAIN_MENU_BG)
        self.game = obj
        self.lang = self.game.lang_manager
        self._stats_loaded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.panel = MenuPlatform()

        self.title = PixelTextWidget(self.lang.get("lvl_complete"), TITLE_FONT_SIZE, MAIN_FONT, self.panel)
        self.title.set_effects(shadow=True)

        label_text_size = 10
        self.wpm_label = PixelTextWidget(font_size=label_text_size, font_path=MAIN_FONT, parent=self.panel)
        self.wpm_label.set_effects(alignment=Qt.AlignmentFlag.AlignLeft)
        self.acc_label = PixelTextWidget(font_size=label_text_size, font_path=MAIN_FONT, parent=self.panel)
        self.acc_label.set_effects(alignment=Qt.AlignmentFlag.AlignLeft)
        self.timer_label = PixelTextWidget(font_size=label_text_size, font_path=MAIN_FONT, parent=self.panel)
        self.timer_label.set_effects(alignment=Qt.AlignmentFlag.AlignLeft)

        self.btn_try_again = PixelButton(self.lang.get("btn_try_again"), self.panel)
        self.btn_statics = PixelButton(self.lang.get("btn_stats"), self.panel)
        self.btn_menu = PixelButton(self.lang.get("btn_main_menu"), self.panel)

        self.btn_try_again.clicked.connect(self.restart_game)
        self.btn_statics.clicked.connect(self.open_stats)
        self.btn_menu.clicked.connect(self.back_to_menu)
        self.lang.language_changed.connect(self.update_ui)
        self.update_ui()

        self.panel.addWidget(self.wpm_label)
        self.panel.addWidget(self.acc_label)
        self.panel.addWidget(self.timer_label)
        self.panel.addWidget(self.btn_try_again)
        self.panel.addWidget(self.btn_statics)
        self.panel.addWidget(self.btn_menu)

        self.update_ui()

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

    def restart_game(self):
        """
        Функция для новой игры
        """
        self.game.sound_player.play("click")
        self.game.set_state(States.PLAYING)

    def open_stats(self):
        """
        Функция для открытия статистики
        """
        self.game.sound_player.play("click")
        self.game.stats_overlay = False
        self.game.set_state(States.STATS)

    def back_to_menu(self):
        """
        Функция для возврата обратно в главное меню
        """
        self.game.sound_player.play("click")
        self.game.set_state(States.MAIN_MENU)

    def update_final_stats(self):
        """
        Функция для подсчета финальной статистики
        """
        self._stats_loaded = True
        self.wpm_label.setText(f"WPM: {self.game.stats.final_wpm}")
        self.acc_label.setText(f"{self.lang.get('acc')}: {self.game.stats.final_accuracy}%")
        self.timer_label.setText(f"{self.lang.get('time')}: {self.game.stats.format_time(self.game.stats.final_time)}")

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """
        self.btn_try_again.setText(self.lang.get("btn_try_again"))
        self.btn_statics.setText(self.lang.get("btn_stats"))
        self.btn_menu.setText(self.lang.get("btn_main_menu"))
        self.title.setText(self.lang.get("lvl_complete"))

        if not self._stats_loaded:
            self.wpm_label.setText("WPM: 000")
            self.acc_label.setText(f"{self.lang.get('acc')}: 100.0%")
            self.timer_label.setText(f"{self.lang.get('time')}: 00:00")
        else:
            self.update_final_stats()