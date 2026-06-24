from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QPainter

from Configuration import *
from ui.components.Button import PixelButton
from ui.components.MenuPlatform import MenuPlatform
from ui.components.Slider import PixelSlider
from ui.components.ComboBox import PixelComboBox
from ui.components.Background import BackgroundPage
from ui.components.TextLineWidget import PixelTextWidget

class SettingsScreen(BackgroundPage):
    """
    Класс экрана настроек
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.game = obj
        self.lang = self.game.lang_manager
        self.blurred = None
        self.is_updating_ui = False
        font_size = TITLE_FONT_SIZE // 2
        main_font = MAIN_FONT

        self.mode_names = [
            (WindowMode.WINDOWED, "wm_windowed"),
            (WindowMode.FULLSCREEN, "wm_fullscreen")
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.panel = MenuPlatform()

        self.title = PixelTextWidget(self.lang.get("title_settings"), TITLE_FONT_SIZE, main_font, self.panel)
        self.title.set_effects(shadow=True)
        self.vol_label = PixelTextWidget(f"{self.lang.get('volume')} {int(self.game.vol_value)}%", font_size, main_font, self.panel)
        self.mus_label = PixelTextWidget(f"{self.lang.get('music')} {int(self.game.mus_value)}%", font_size, main_font, self.panel)
        self.lang_label = PixelTextWidget(self.lang.get('lang'), font_size, main_font, self.panel)
        self.window_mode = PixelTextWidget(self.lang.get("window_mode"), font_size, main_font, self.panel)

        self.vol_slider = PixelSlider()
        self.mus_slider = PixelSlider()
        self.lang_combo = PixelComboBox()

        self.btn_back = PixelButton(self.lang.get("btn_back"), self.panel)

        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self.game.vol_value))
        self.vol_slider.setFixedWidth(280)
        self.vol_slider.valueChanged.connect(self.update_volume)

        self.mus_slider.setRange(0, 100)
        self.mus_slider.setValue(int(self.game.mus_value))
        self.mus_slider.setFixedWidth(280)
        self.mus_slider.valueChanged.connect(self.update_music)

        self.mode_combo = PixelComboBox()
        current_mode_index = list(WindowMode).index(self.game.screen_mode)

        self.lang_data = self.game.lang_data
        lang_names = [lang[1] for lang in self.lang_data]
        current_lang_code = self.game.lang_manager.lang
        current_lang_index = [lang[0] for lang in self.lang_data].index(current_lang_code)

        self.setup_combo(self.mode_combo, [], current_mode_index, self.change_screen_mode)
        self.setup_combo(self.lang_combo, lang_names, current_lang_index, self.change_language)

        self.btn_back.clicked.connect(self.back_to_menu)

        self.lang.language_changed.connect(self.update_ui)

        self.vol_slider.valueChanged.connect(self.update_volume)
        self.vol_slider.valueChanged.connect(self.game.sound_player.set_volume)
        self.mus_slider.valueChanged.connect(self.update_music)
        self.mus_slider.valueChanged.connect(self.game.music_player.set_volume)
        
        self.panel.layout.addWidget(self.mus_label)
        self.panel.layout.addWidget(self.mus_slider)
        self.panel.layout.addWidget(self.vol_label)
        self.panel.layout.addWidget(self.vol_slider)
        self.panel.layout.addWidget(self.lang_label)
        self.panel.layout.addWidget(self.lang_combo)
        self.panel.layout.addWidget(self.window_mode)
        self.panel.layout.addWidget(self.mode_combo)
        self.panel.layout.addWidget(self.btn_back)

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
    
    def update_volume(self, value):
        """
        Функция для изменения громкости звука игры
        """
        self.vol_label.setText(f"{self.lang.get('volume')} {value}%")
        self.game.vol_value = value
        self.game.settings["volume"] = value
    def update_music(self, value):
        """
        Функция для изменения музыки звука игры
        """
        self.mus_label.setText(f"{self.lang.get('music')} {value}%")
        self.game.mus_value = value
        self.game.settings["music"] = value

    def change_screen_mode(self, index):
        """
        Функция для изменения типа экрана
        """
        if index < 0 or self.is_updating_ui:
            return
        mode_list = list(WindowMode)
        self.game.screen_mode = mode_list[index]
        self.game.fullscreen = (self.game.screen_mode == WindowMode.FULLSCREEN)

        self.game.settings["screen_mode_index"] = index
        self.game.settings["window_mode"] = self.game.screen_mode.name
        self.game.settings["fullscreen"] = self.game.fullscreen
        self.game.set_screen_mode()

    def change_language(self, index):
        """
        Функция для изменения языка игры
        """
        if index < 0 or self.is_updating_ui:
            return
            
        lang_code = self.lang_data[index][0]
        
        self.lang.set_lang(lang_code)
        
        self.game.settings["language"] = lang_code
        self.game.save_settings()
        
        self.lang.language_changed.emit()
        
        self.update_ui()

    def back_to_menu(self):
        """
        Функция для возврата обратно в меню из настроек
        """
        self.game.sound_player.play("click")
        self.game.save_settings()
        if self.game.settings_pause_overlay:
            self.game.set_state(States.PAUSE_MENU)
        else:
            self.game.set_state(States.MAIN_MENU)

    def update_ui(self):
        """
        Функция для обновления текста на экране при смене языка
        """

        if self.is_updating_ui:
            return

        self.is_updating_ui = True
        try:
            self.lang_data = self.game.lang_manager.get_list()
            lang_names = [name for _, name in self.lang_data]

            self.lang_combo.blockSignals(True)
            self.lang_combo.clear()
            self.lang_combo.addItems(lang_names)

            current_code = self.lang.lang
            current_lang_index = [lang[0] for lang in self.lang_data].index(current_code)
            self.lang_combo.setCurrentIndex(current_lang_index)
            self.lang_combo.blockSignals(False)
        
            self.mode_combo.blockSignals(True)
            self.mode_combo.clear()

            translated_modes = [self.lang.get(key) for _, key in self.mode_names]
            self.mode_combo.addItems(translated_modes)

            current_index = list(WindowMode).index(self.game.screen_mode)
            self.mode_combo.setCurrentIndex(current_index)
            self.mode_combo.blockSignals(False)

            self.vol_label.setText(f"{self.lang.get('volume')} {int(self.game.vol_value)}%")
            self.mus_label.setText(f"{self.lang.get('music')} {int(self.game.mus_value)}%")
            self.lang_label.setText(self.lang.get("lang"))
            self.window_mode.setText(self.lang.get("window_mode"))
            self.btn_back.setText(self.lang.get("btn_back"))
            self.title.setText(self.lang.get("title_settings"))
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