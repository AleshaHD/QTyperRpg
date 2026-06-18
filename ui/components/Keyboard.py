import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QPoint

from Configuration import *
from ui.components.TextLineWidget import load_font

class LeftHandWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class RightHandWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class VirtualKeyboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layout = 'ru'
        self.highlighted_buttons = []
        self.grid_buttons = []
        self.setMinimumSize(400, 150)

        self.pixel_font = QFont(load_font(MAIN_FONT), 10)
        self.sys_font = QFont(load_font(MAIN_FONT), 8)

        self.finger_map = {
            0: set("йфя12ёqaz@!"),       # Л. мизинец
            1: set("цыч3wsx#"),          # Л. безымянный
            2: set("увк4edc$"),          # Л. средний
            3: set("кеапмч56rtfgvb%^"),  # Л. указательный
            4: set(" "),                 # Л. большой (пробел)
            5: set(" "),                 # П. большой (пробел)
            6: set("нгоьт78yuhjnm&*"),   # П. указательный
            7: set("шлб9eik,("),         # П. средний
            8: set("щдю0olj.)"),         # П. безымянный
            9: set("зхъжэ.0-=p[;']_+\x0b") # П. мизинец + системные справа
        }

        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_base = os.path.abspath(os.path.join(current_dir, "../..", "assets", "images", "hands"))

        self.left_hand_sprites = {
            frozenset(): QPixmap(os.path.join(assets_base, "l", "l_hand.png")),
            frozenset([4]): QPixmap(os.path.join(assets_base, "l", "l_hand_thumb.png")),    
            frozenset([3]): QPixmap(os.path.join(assets_base, "l", "l_hand_index.png")),    
            frozenset([2]): QPixmap(os.path.join(assets_base, "l", "l_hand_middle.png")),    
            frozenset([1]): QPixmap(os.path.join(assets_base, "l", "l_hand_ring.png")),  
            frozenset([0]): QPixmap(os.path.join(assets_base, "l", "l_hand_little.png"))    
        }
        self.right_hand_sprites = {
            frozenset(): QPixmap(os.path.join(assets_base, "r", "r_hand.png")),
            frozenset([5]): QPixmap(os.path.join(assets_base, "r", "r_hand_thumb.png")),
            frozenset([6]): QPixmap(os.path.join(assets_base, "r", "r_hand_index.png")),
            frozenset([7]): QPixmap(os.path.join(assets_base, "r", "r_hand_middle.png")),
            frozenset([8]): QPixmap(os.path.join(assets_base, "r", "r_hand_ring.png")),
            frozenset([9]): QPixmap(os.path.join(assets_base, "r", "r_hand_little.png"))
        }

        self.current_left_fingers = set()
        self.current_right_fingers = set()

        self.left_hand_label = LeftHandWidget(self.parent())
        self.right_hand_label = RightHandWidget(self.parent())

        self.left_hand_label.hide()
        self.right_hand_label.hide()

        self.setup_ui()

    def update_hand_pixmaps(self):
        hand_w = self.left_hand_label.width()
        hand_h = self.left_hand_label.height()

        if hand_w <= 0 or hand_h <= 0:
            return

        left_key = frozenset(self.current_left_fingers)
        left_pixmap = self.left_hand_sprites.get(left_key, self.left_hand_sprites[frozenset()])
        if not left_pixmap.isNull():
            self.left_hand_label.setPixmap(left_pixmap.scaled(hand_w, hand_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        right_key = frozenset(self.current_right_fingers)
        right_pixmap = self.right_hand_sprites.get(right_key, self.right_hand_sprites[frozenset()])
        if not right_pixmap.isNull():
           self.right_hand_label.setPixmap(right_pixmap.scaled(hand_w, hand_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def get_btn_style(self, bg_color, is_system=False):
        border_color = "#78909c" if is_system else "#90a4ae"
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: #000000;
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px;
            }}
        """

    def get_finger_zone(self, row, col, key_id):
        if key_id == "Space":
            return 4, self.finger_colors[4]
        
        if row < len(self.keyboard_zone_matrix) and col < len(self.keyboard_zone_matrix[row]):
            finger = self.keyboard_zone_matrix[row][col]
            if finger != -1:
                return finger, self.finger_colors[finger]
                
        return -1, "#e0e0e0"

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.kb_container = QWidget()
        self.kb_container.setStyleSheet(
            "background-color: #bdc3c7; border: 2px solid #95a5a6; border-radius: 4px;"
        )

        self.main_layout.addWidget(self.kb_container)

        kb_layout = QVBoxLayout(self.kb_container)
        kb_layout.setSpacing(1)
        kb_layout.setContentsMargins(4, 4, 4, 4)

        self.en_normal = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
            ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
            ["Caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
            ["L_Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "R_Shift"],
            ["Ctrl", "Cmd", "Alt", "Space", "Alt", "Cmd", "Menu", "Ctrl"]
        ]
        self.en_shift = [
            ["~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "Backspace"],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{", "}", "|"],
            ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ":", "\"", "Enter"],
            ["L_Shift", "Z", "X", "C", "V", "B", "N", "M", "<", ">", "?", "R_Shift"],
            ["Ctrl", "Cmd", "Alt", "Space", "Alt", "Cmd", "Menu", "Ctrl"]
        ]
        self.ru_normal = [
            ["ё", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
            ["Tab", "й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ", "\\"],
            ["Caps", "ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э", "Enter"],
            ["L_Shift", "я", "ч", "с", "м", "и", "т", "ь", "б", "ю", ".", "R_Shift"],
            ["Ctrl", "Cmd", "Alt", "Space", "Alt", "Cmd", "Menu", "Ctrl"]
        ]
        self.ru_shift = [
            ["Ё", "!", "\"", "№", ";", "%", "*", "(", ")", "_", "+", "Backspace"],
            ["Tab", "Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З", "Х", "Ъ", "/"],
            ["Caps", "Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д", "Ж", "Э", "Enter"],
            ["L_Shift", "Я", "Ч", "С", "М", "И", "Т", "Ь", "Б", "Ю", ",", "R_Shift"],
            ["Ctrl", "Cmd", "Alt", "Space", "Alt", "Cmd", "Menu", "Ctrl"]
        ]

        self.finger_colors = {
            0: "#f5b5b5",  # Л. мизинец (Розово-красный)
            1: "#f0e1b1",  # Л. безымянный (Песочно-желтый)
            2: "#c7e9b4",  # Л. средний (Нежно-зеленый)
            3: "#9ecae1",  # Л. указательный (Голубой)
            4: "#c7c7f5",  # Л. большой (Лилово-синий для Пробела)
            5: "#c7c7f5",  # П. большой (Лилово-синий для Пробела)
            6: "#d7b5d8",  # П. указательный (Сиреневый)
            7: "#dfa8a8",  # П. средний (Розовато-терракотовый)
            8: "#d9f0a3",  # П. безымянный (Салатовый)
            9: "#addd8e"   # П. мизинец (Светло-зеленый)
        }

        self.keyboard_zone_matrix = [
            [0, 0, 0, 1, 2, 3, 3, 6, 7, 8, 9, 9, 9, -1],
            [-1, 0, 1, 2, 3, 3, 6, 6, 7, 8, 9, 9, 9, 9],
            [-1, 0, 1, 2, 3, 3, 6, 6, 7, 8, 9, 9, -1],
            [-1, 0, 1, 2, 3, 3, 6, 6, 7, 8, 9, -1],
            [-1, -1, -1, 4, -1, -1, -1, -1]
        ]

        self.system_keys = {"Backspace", "Tab", "Caps", "L_Shift", "R_Shift", "Enter", "Ctrl", "Cmd", "Alt", "Space", "Win", "Menu"}

        current_matrix = self.ru_normal if self.current_layout == 'ru' else self.en_normal

        for r_idx in range(5):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)
            row_buttons = []
            
            for c_idx, key_id in enumerate(current_matrix[r_idx]):
                btn_text = "Shift" if "Shift" in key_id else key_id
                button = QPushButton(btn_text)
                button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                
                is_sys = key_id in self.system_keys
                button.setFont(self.sys_font if is_sys else self.pixel_font)
                button.setSizePolicy(button.sizePolicy().horizontalPolicy(), button.sizePolicy().verticalPolicy().Expanding)
                
                btn_w = 10
                if key_id == "Backspace": btn_w = 20
                elif key_id == "Tab": btn_w = 15
                elif key_id == "Caps": btn_w = 18
                elif key_id == "Enter": btn_w = 22
                elif "Shift" in key_id: btn_w = 25
                elif key_id == "Space": btn_w = 75
                elif key_id in ("Ctrl", "Alt", "Cmd"): btn_w = 13
                
                _, zone_color = self.get_finger_zone(r_idx, c_idx, key_id)
                button.setStyleSheet(self.get_btn_style(zone_color, is_sys))
                
                row_layout.addWidget(button, stretch=btn_w)
                row_buttons.append(button)
                    
            self.grid_buttons.append(row_buttons)
            kb_layout.addLayout(row_layout)

    def set_key_color_by_coords(self, row, col, color):
        """
        Функция для окрашивания клавиш по её координатам в матрице и сохранения оригинальн цвета
        """
        if 0 <= row < len(self.grid_buttons) and 0 <= col < len(self.grid_buttons[row]):
            button = self.grid_buttons[row][col]
            
            current_matrix = self.ru_normal if self.current_layout == 'ru' else self.en_normal
            key_id = current_matrix[row][col]
            is_sys = key_id in self.system_keys
            
            _, original_color = self.get_finger_zone(row, col, key_id)
            
            if not any(highlighted[0] == button for highlighted in self.highlighted_buttons):
                self.highlighted_buttons.append((button, original_color, is_sys))
                
            button.setStyleSheet(self.get_btn_style(color, is_sys))

    def set_key_color_by_id(self, key_id, color):
        """
        Функция для нахождения клавиш по её текстовому ID и закрашивания ее
        """
        current_matrix = self.ru_normal if self.current_layout == 'ru' else self.en_normal
        
        for r in range(len(current_matrix)):
            for c in range(len(current_matrix[r])):
                if current_matrix[r][c] == key_id:
                    self.set_key_color_by_coords(r, c, color)
                    return

    def get_finger_for_char(self, char: str):
        if not char: return -1
        char_lower = char.lower()
        for finger, chars in self.finger_map.items():
            if char_lower in chars:
                if char == " ": 
                    return 4
                return finger
        return -1

    def switch_layout(self, layout='en'):
        self.current_layout = layout
        self.clear_highlight()
        current_matrix = self.ru_normal if layout == 'ru' else self.en_normal

        for r in range(len(self.grid_buttons)):
            for c in range(len(self.grid_buttons[r])):
                btn_id = current_matrix[r][c]
                button = self.grid_buttons[r][c]
                if btn_id not in self.system_keys:
                    button.setText(btn_id.upper())

    def highlight_next_char(self, char):
        self.clear_highlight() 
        
        self.current_left_fingers = []
        self.current_right_fingers = []

        if not char:
            self.update_hand_pixmaps()
            return

        if char == " ":
            self.set_key_color_by_id("Space", "#ff3333") 
            self.current_left_fingers = [4]
            self.update_hand_pixmaps()
            return

        normal_matrix = self.ru_normal if self.current_layout == 'ru' else self.en_normal
        shift_matrix = self.ru_shift if self.current_layout == 'ru' else self.en_shift
        
        row, col = -1, -1
        requires_shift = False

        for r in range(len(normal_matrix)):
            if char in normal_matrix[r]:
                row, col = r, normal_matrix[r].index(char)
                requires_shift = False
                break
        
        if row == -1:
            for r in range(len(shift_matrix)):
                if char in shift_matrix[r]:
                    row, col = r, shift_matrix[r].index(char)
                    requires_shift = True
                    break
                    
        if row == -1 and char.lower() != char:
            for r in range(len(normal_matrix)):
                if char.lower() in normal_matrix[r]:
                    row, col = r, normal_matrix[r].index(char.lower())
                    requires_shift = True
                    break

        if row != -1 and col != -1:
            zone = self.keyboard_zone_matrix[row][col]
            
            self.set_key_color_by_coords(row, col, "#ff3333")
            
            if zone != -1:
                if zone <= 4:
                    self.current_left_fingers = [zone]
                else:
                    self.current_right_fingers = [zone]
            
            if requires_shift and zone != -1:
                if zone <= 4:
                    self.set_key_color_by_id("R_Shift", "#ff3333")
                    self.current_right_fingers = [9]
                else:
                    self.set_key_color_by_id("L_Shift", "#ff3333")
                    self.current_left_fingers = [0]

        self.update_hand_pixmaps()

    def clear_highlight(self):
        for button, original_color, is_sys in self.highlighted_buttons:
            button.setStyleSheet(self.get_btn_style(original_color, is_sys))
        self.highlighted_buttons.clear()
        
        self.current_left_fingers.clear()
        self.current_right_fingers.clear()
        self.update_hand_pixmaps()

    def resize_hands(self):
        if self.width() <= 1 or self.height() <= 1:
                return

        parent = self.parentWidget()
        if parent is None:
            return

        kb_pos = self.mapToParent(QPoint(0, 0))
        kb_x, kb_y = kb_pos.x(), kb_pos.y()
        kb_w, kb_h = self.width(), self.height()

        parent_w = parent.width()

        left_space = kb_x
        right_space = parent_w - (kb_x + kb_w)
        side_space = min(left_space, right_space)

        if side_space < 120:
            self.left_hand_label.hide()
            self.right_hand_label.hide()
            return

        self.left_hand_label.show()
        self.right_hand_label.show()

        size_from_height = int(kb_h * 1.05)
        size_from_side = int(side_space * 0.92)
        hand_size = min(size_from_height, size_from_side, 260)

        if hand_size < 80:
            self.left_hand_label.hide()
            self.right_hand_label.hide()
            return

        hand_width = hand_height = hand_size
        gap = max(8, int(hand_width * 0.05))
        hand_y = max(0, kb_y - int(hand_height * 0.12))

        left_x = max(0, kb_x - hand_width - gap)
        right_x = min(parent_w - hand_width, kb_x + kb_w + gap)

        self.left_hand_label.setGeometry(left_x, hand_y, hand_width, hand_height)
        self.right_hand_label.setGeometry(right_x, hand_y, hand_width, hand_height)

        self.update_hand_pixmaps()