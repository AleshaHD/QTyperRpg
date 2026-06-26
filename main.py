import sys, os, json, ctypes
from PySide6.QtWidgets import QMainWindow, QApplication, QStackedWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from Configuration import *

from ui.screens.MainMenu import MainMenu
from ui.screens.SettingsScreen import SettingsScreen
from ui.screens.GameScreen import GameScreen
from ui.screens.PauseScreen import PauseScreen
from ui.screens.EndScreen import EndScreen
from ui.screens.SessionScreen import SelectSession

from core.TextLoader import TextLoader
from core.Music import MusicPlayer, SoundPlayer
from logic.GameStats import GameStats
from ui.screens.StatsScreen import StatsHistory, StatsScreen

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.mygame.jrpggame.1.0')
except AttributeError:
    pass

class Game(QMainWindow):
    """
    Основной класс игры
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTyper")
        self.setWindowIcon(QIcon(WIN_ICON))
        self.setMinimumSize(640, 515)

        self.settings_pause_overlay = False
        self.stats_overlay = False

        self.current_difficulty = Difficult.EASY
        self.current_lang_layout = "ru"

        self.settings = self.load_settings()
        self.lang_manager = LANG_MANAGER
        self.lang_manager.set_lang(self.settings.get("language", "ru"))
        self.lang_data = self.lang_manager.get_list()
        self.res_index = self.settings.get("res_index", 0)
        self.w = self.settings.get("width", 800)
        self.h = self.settings.get("height", 600)
        self.fullscreen = self.settings.get("fullscreen", False)
        self.vol_value = self.settings.get("volume", 100)
        self.mus_value = self.settings.get("music", 100)

        screen_mode_index = self.settings.get("screen_mode_index", WindowMode.WINDOWED.value)
        self.screen_mode = list(WindowMode)[screen_mode_index]
       
        self.file = TextLoader(self)
        self.stats = GameStats()

        self.music_player = MusicPlayer(self.mus_value)
        self.music_player.play_track(MENU_MUSIC)

        self.sound_player = SoundPlayer(self.vol_value)
        self.sound_player.add_sound("click", BUTTON_SOUND)

        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
           
        self.menu_screen = MainMenu(self)
        self.game_screen = GameScreen(self)
        self.end_screen = EndScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.settings_screen.setParent(self)
        self.settings_screen.resize(self.size())
        self.settings_screen.hide()
        self.pause_screen = PauseScreen(self)
        self.pause_screen.setParent(self)
        self.pause_screen.resize(self.size())
        self.pause_screen.hide()
        self.stats_history = StatsHistory()
        self.stats_screen = StatsScreen(self)
        self.stats_screen.setParent(self)
        self.stats_screen.resize(self.size())
        self.stats_screen.hide()
        self.select_session = SelectSession(self)
        self.select_session.setParent(self)
        self.select_session.resize(self.size())
        self.select_session.hide()

        self.stacked_widget.addWidget(self.menu_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.end_screen)

        self.previous_state = None
        self.state = States.MAIN_MENU
        self.set_state(States.MAIN_MENU)
        self.resize(self.w, self.h)
        self.set_screen_mode()

    def center_on_screen(self):
        """
        Функция для получения координат центра экрана
        """
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.w) // 2
        y = (screen.height() - self.h) // 2
        self.move(x, y)

    def set_state(self, new_state):
        """
        Функция для переключения между состояниями игры
        """
        self.menu_screen.menu_container.show()
        self.pause_screen.hide()
        self.stats_screen.hide()
        self.select_session.hide()
        self.settings_screen.hide()

        self.previous_state = self.state
        self.state = new_state

        # Состояние "Главное меню"
        if self.state == States.MAIN_MENU:
            self.music_player.play_track(MENU_MUSIC)
            self.pause_screen.hide()
            self.stacked_widget.setCurrentWidget(self.menu_screen)

        # Состояние "Меню настроек"
        elif self.state == States.SETTINGS:
            self.pause_screen.hide()
            self.settings_screen.setGeometry(0, 0, self.width(), self.height())
            self.settings_screen.show()
            self.settings_screen.raise_()
            self.settings_screen.setFocus()

            if self.previous_state in (States.PAUSE_MENU, States.PLAYING):
                self.settings_pause_overlay = True
                self.stacked_widget.setCurrentWidget(self.game_screen)
                self.music_player.pause()
            else:
                self.settings_pause_overlay = False
                self.menu_screen.menu_container.hide()
                self.stacked_widget.setCurrentWidget(self.menu_screen)
                self.music_player.play_track(MENU_MUSIC)

        # Состояние "Экран игры"
        elif self.state == States.PLAYING:
            self.pause_screen.hide()
            self.game_screen.setFocus()
            self.stacked_widget.setCurrentWidget(self.game_screen)

            if self.previous_state == States.PAUSE_MENU or \
               (self.previous_state == States.SETTINGS and self.settings_pause_overlay) or \
               (self.previous_state == States.STATS and self.stats_overlay):
                self.music_player.resume()
            else:
                self.music_player.play_track(GAME_MUSIC)
            if self.previous_state == States.SELECT_SESSION or \
                self.previous_state != States.PAUSE_MENU and not \
                (self.previous_state == States.STATS and self.stats_overlay):
                self.game_screen.start_session()
            else:
                self.stats.end_pause()

        # Состояние "Меню выбора"
        elif self.state == States.SELECT_SESSION:
            self.music_player.play_track(MENU_MUSIC)
            self.pause_screen.hide()
            self.settings_screen.hide()
            self.stats_screen.hide()
            self.stacked_widget.setCurrentWidget(self.menu_screen)
            self.select_session.setGeometry(0, 0, self.width(), self.height())
            self.menu_screen.menu_container.hide()
            self.select_session.show()
            self.select_session.raise_()
            self.select_session.setFocus()

        # Состояние "Меню паузы"
        elif self.state == States.PAUSE_MENU:
            self.music_player.pause()
            if self.previous_state == States.PLAYING:
                self.stats.start_pause()
            self.stacked_widget.setCurrentWidget(self.game_screen)
            self.pause_screen.show()
            self.pause_screen.raise_()
            self.pause_screen.setFocus()

        # Состояние "Экран конца"
        elif self.state == States.END_SCREEN:
            self.music_player.stop()
            self.pause_screen.hide()
            self.end_screen.setGeometry(0, 0, self.width(), self.height())
            if self.previous_state != States.STATS:
                self.end_screen.update_final_stats()
            self.stacked_widget.setCurrentWidget(self.end_screen)

        # Состояние "Экран статистики"
        elif self.state == States.STATS:
            self.pause_screen.hide()
            self.music_player.pause()
            self.stats_return_state = self.previous_state
            if self.previous_state in (States.PAUSE_MENU, States.PLAYING):
                self.stats_overlay = True
                self.stacked_widget.setCurrentWidget(self.game_screen)
            else:
                self.stats_overlay = False
                self.menu_screen.menu_container.hide()
                self.stacked_widget.setCurrentWidget(self.menu_screen)

            self.stats_screen.setGeometry(0, 0, self.width(), self.height())
            self.stats_screen.refresh_stats()
            self.stats_screen.show()
            self.stats_screen.raise_()
            self.stats_screen.setFocus()

    def set_screen_mode(self):
        """
        Функция для изменения типа экрана
        """
        if self.screen_mode == WindowMode.FULLSCREEN:
            self.setWindowFlags(Qt.WindowType.Window)
            self.showFullScreen()
        else:
            self.setWindowFlags(Qt.WindowType.Window)
            self.showNormal()

            current_screen = self.screen()
            if current_screen:
                avail = current_screen.availableGeometry()

                display_w = min(self.w, avail.width() - 16)
                display_h = min(self.h, avail.height() - 39)
            else:
                display_w, display_h = self.w, self.h
            self.resize(display_w, display_h)
            self.center_on_screen()

        current_size = self.size()
        self.pause_screen.resize(current_size)

        if self.settings_screen and self.settings_screen.isVisible():
            self.settings_screen.setGeometry(0, 0, self.width(), self.height())
            self.settings_screen.raise_()

        for screen in (self.menu_screen, self.settings_screen, self.game_screen, self.end_screen):
            if screen:
                screen.reset_particles()

        self.stacked_widget.updateGeometry()
        self.stacked_widget.repaint()
        self.update()

    def change_language(self, lang):
        self.settings["language"] = lang
        self.lang_manager.set_lang(lang)
        self.save_settings()
        self.lang_manager.language_changed.emit()

    def restart_game(self):
        """
        Функция для рестарта игры
        """
        self.music_player.play_track(GAME_MUSIC)
        self.pause_screen.hide()
        self.stats.reset("")
        self.previous_state = None
        self.state = States.PLAYING
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.game_screen.start_session()
        self.game_screen.setFocus()
    
    def finish_level(self):
        """
        Функция для завершения уровня
        """
        self.game_screen.ui_timer.stop()
        self.stats.finish_timer()
        self.stats.save_final_stats()
        self.stats_history.add_match(self.stats.final_wpm, self.stats.final_accuracy, self.stats.final_time)
        self.set_state(States.END_SCREEN)

    def load_settings(self):
        """
        Функция для загрузки настроек пользователя
        """
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception:
                pass
        return {"volume": 100,
                "music": 100,
                "res_index": 0,
                "width": 800,
                "height": 600,
                "fullscreen": False,
                "screen_mode_index": WindowMode.WINDOWED.value,
                "language": "ru"
                }

    def save_settings(self):
        """
        Функция для сохранения настроек пользователя
        """
        ensure_dir_exists(SAVE_FILE)
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def change_lang(self, lang):
        self.settings["language"] = lang
        self.lang_manager.set_lang(lang)
        self.file.set_language(lang)
        self.save_settings()
        self.lang_manager.language_changed.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.state == States.SETTINGS:
                if self.settings_pause_overlay:
                    self.set_state(States.PAUSE_MENU)
                else:
                    self.set_state(States.MAIN_MENU)
                return
            elif self.state == States.PAUSE_MENU:
                self.set_state(States.PLAYING)
                return
            elif self.state == States.STATS:
                if hasattr(self, 'stats_return_state') and self.stats_return_state:
                    self.set_state(self.stats_return_state)
                else:
                    self.set_state(States.MAIN_MENU)
                return
            elif self.state == States.SELECT_SESSION:
                self.set_state(States.MAIN_MENU)
                return
        if self.state == States.PLAYING:
            self.game_screen.handle_key(event)
        if event.key() == Qt.Key.Key_F11:
            if self.screen_mode == WindowMode.FULLSCREEN:
                self.screen_mode = WindowMode.WINDOWED
            else:
                self.screen_mode = WindowMode.FULLSCREEN
            current_index = list(WindowMode).index(self.screen_mode)
            self.settings["screen_mode_index"] = current_index
            self.settings["window_mode"] = self.screen_mode.name
            self.settings["fullscreen"] = (self.screen_mode == WindowMode.FULLSCREEN)
            self.set_screen_mode()
            if self.settings_screen:
                self.settings_screen.update_ui()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.pause_screen.resize(self.size())
        self.settings_screen.resize(self.size())
        self.stats_screen.resize(self.size())
        self.end_screen.resize(self.size())
        self.select_session.resize(self.size())

    def closeEvent(self, event):
        if not self.isFullScreen():
            self.settings["width"] = self.width()
            self.settings["height"] = self.height()
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Game()
    window.show()
    app.exec()