from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QPainter

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.ComboBox import PixelComboBox
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class SelectSession(BackgroundPage):
    """
    Класс начального экрана
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.game = obj
        self.lang = self.game.lang_manager
        font_size = TITLE_FONT_SIZE // 2
        main_font = MAIN_FONT
        self.is_updating_ui = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.panel = MenuPlatform()

        self.lang_combo = PixelComboBox()
        self.difficult_combo = PixelComboBox()

        self.difficult_names = [
            (Difficult.EASY, "diff_easy"),
            (Difficult.NORMAL, "diff_normal"),
            (Difficult.HARD, "diff_hard")
        ]

        self.lang_options = self.lang.get_list()
        self.diff_options = [(d.name, d.name.capitalize()) for d in Difficult]

        lang_names = [item[1] for item in self.lang_options]
        difficult_names = [item[1] for item in self.diff_options]

        self.setup_combo(self.lang_combo, lang_names, 0, self.on_lang_changed)
        self.setup_combo(self.difficult_combo, difficult_names, 0, self.on_difficult_changed)

        self.title = PixelTextWidget(self.lang.get("title_select_session"), TITLE_FONT_SIZE, main_font, self.panel)
        self.title.set_effects(shadow=True)
        self.lang_label = PixelTextWidget(self.lang.get('lang_layout'), font_size, main_font, self.panel)
        self.difficult_label = PixelTextWidget(self.lang.get('difficult'), font_size, main_font, self.panel)

        self.btn_start = PixelButton(self.lang.get("btn_start"), self.panel)
        self.btn_back = PixelButton(self.lang.get("btn_back"), self.panel)

        self.btn_start.clicked.connect(self.start_game)
        self.btn_back.clicked.connect(self.back_to_menu)
        self.lang.language_changed.connect(self.update_ui)

        self.panel.layout.addWidget(self.lang_label)
        self.panel.layout.addWidget(self.lang_combo)
        self.panel.layout.addWidget(self.difficult_label)
        self.panel.layout.addWidget(self.difficult_combo)
        self.panel.layout.addWidget(self.btn_start)
        self.panel.layout.addWidget(self.btn_back)

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
        self.update_ui()

    def setup_combo(self, combo, items, current_index, callback):
        """
        Функция для соединения ComboBox
        """
        combo.setFixedWidth(280)
        combo.addItems(items)
        combo.setCurrentIndex(current_index)
        combo.currentIndexChanged.connect(callback)
        return combo

    def start_game(self):
        self.game.sound_player.play("click")
        self.game.set_state(States.PLAYING)

    def back_to_menu(self):
        """
        Функция для возврата обратно в главное меню
        """
        self.game.sound_player.play("click")
        self.game.save_settings()
        self.game.set_state(States.MAIN_MENU)

    def on_lang_changed(self, index):
        code = self.lang_options[index][0]
        self.game.current_lang_layout = code
        self.game.game_screen.keyboard.switch_layout(code)

    def on_difficult_changed(self, index):
        selected_diff = list(Difficult)[index]
        self.game.current_difficulty = selected_diff

    def update_ui(self):
        if self.is_updating_ui:
            return

        self.is_updating_ui = True
        try:
            self.lang_options = self.lang.get_list()
            lang_names = [item[1] for item in self.lang_options]

            self.lang_combo.blockSignals(True)
            self.lang_combo.clear()
            self.lang_combo.addItems(lang_names)

            current_code = self.game.current_lang_layout
            current_idx = next((i for i, item in enumerate(self.lang_options) if item[0] == current_code), 0)
            self.lang_combo.setCurrentIndex(current_idx)
            self.lang_combo.blockSignals(False)

            self.difficult_combo.blockSignals(True)
            self.difficult_combo.clear()
            
            translated_diffs = [self.lang.get(key) for _, key in self.difficult_names]
            self.difficult_combo.addItems(translated_diffs)
            
            current_diff_idx = list(Difficult).index(self.game.current_difficulty)
            self.difficult_combo.setCurrentIndex(current_diff_idx)
            self.difficult_combo.blockSignals(False)

            self.title.setText(self.lang.get("title_select_session"))
            self.lang_label.setText(self.lang.get('lang_layout'))
            self.difficult_label.setText(self.lang.get('difficult'))
            self.btn_start.setText(self.lang.get("btn_start"))
            self.btn_back.setText(self.lang.get("btn_back"))
        finally:
            self.is_updating_ui = False

    def showEvent(self, event):
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 170))
        finally:
            painter.end()