import os.path
from core.LangManager import LangManager
from enum import Enum, auto
class States(Enum):
    MAIN_MENU = auto()
    SETTINGS = auto()
    SELECT_SESSION = auto()
    PLAYING = auto()
    PAUSE_MENU = auto()
    END_SCREEN = auto()
    STATS = auto()
class WindowMode(Enum):
    WINDOWED = auto()
    FULLSCREEN = auto()
class Difficult(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()

TEST_TEXT = False
TITLE_FONT_SIZE = 24

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED =   (255, 0, 0)
GREEN = (0, 255, 0)
BLUE =  (0, 0, 255)

import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
def get_font_path(path):
    return os.path.normpath(os.path.join(ROOT_DIR, path))
def ensure_dir_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)
def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
APP_DIR = get_app_dir()
USER_DATA_DIR = os.path.join(APP_DIR, "user_data")
SAVE_FILE = os.path.join(USER_DATA_DIR, "config.json")
STATS_FILE = os.path.join(USER_DATA_DIR, "stats.json")

ASSETS_DIR = resource_path("assets/")

GAME_MUSIC = os.path.join(ASSETS_DIR, "sounds/music/In mood (full version).wav")
MENU_MUSIC = os.path.join(ASSETS_DIR, "sounds/music/660655ec5901fb8.mp3")
BUTTON_SOUND = os.path.join(ASSETS_DIR, "sounds/effects/minecraft_click.wav")

MAIN_FONT = os.path.join(ASSETS_DIR, "fonts/minecraft.ttf")
WIN_ICON = os.path.join(ASSETS_DIR, "images/icon.ico")

MAIN_MENU_BG = os.path.join(ASSETS_DIR, "images/bg/main_menu_bg.jpg")

TEXTS_FILES = os.path.join(ASSETS_DIR, "assets/texts")
LANG_FILE = os.path.join(ASSETS_DIR, "lang.csv")

LANG_MANAGER = LangManager(LANG_FILE)
MODE_NAMES = {
    WindowMode.WINDOWED: LANG_MANAGER.get("wm_windowed"),
    WindowMode.FULLSCREEN: LANG_MANAGER.get("wm_fullscreen"),
}

WIN_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1440, 900),
    (1600, 900),
    (1920, 1080)
]

DIFFICULT_NAMES = {
    Difficult.EASY: LANG_MANAGER.get("diff_easy"),
    Difficult.EASY: LANG_MANAGER.get("diff_normal"),
    Difficult.EASY: LANG_MANAGER.get("diff_hard")
}