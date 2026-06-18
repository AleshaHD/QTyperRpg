import math
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtCore import Qt, QSize, QTimer

class MenuPlatform(QFrame):
    """
    Класс для создания подстилки для кнопок в главном меню
    """
    def __init__(self, parent=None, color_hex="#3e414a"):
        super().__init__(parent)
        self.pixel_color = QColor(color_hex)
        self.pixel_size = 4
        self.r = 2

        self.chached_pixmap = QPixmap()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def sizeHint(self):
        base_hint = self.layout.sizeHint()
        if base_hint.isEmpty():
            return QSize(280, 320)

        w = max(280, math.ceil(base_hint.width() / self.pixel_size) * self.pixel_size)
        h = max(320, math.ceil(base_hint.height() / self.pixel_size) * self.pixel_size)
        return QSize(w, h)

    def is_inside_bounds(self, col, row, cols, rows):
        """
        Функция для проверки вхождения пикселя в форму панели с учетом скругления углов
        """
        if col < 0 or col >= cols or row < 0 or row >= rows:
            return False

        # Алгоритм 'квадрагления' углов по краям прямоугольника
        r = self.r
        is_top_left = (col + row) < r
        is_top_right = ((cols - 1 - col) + row) < r
        is_bottom_left = (col + (rows - 1 - row)) < r
        is_bottom_right = ((cols - 1 - col) + (rows - 1 - row)) < r

        if is_top_left or is_top_right or is_bottom_left or is_bottom_right:
            return False
        return True

    def generate_pixels(self):
        """
        Функция для создания пикселей для меню
        """
        if self.width() <= 0 or self.height() <= 0:
            return

        self.chached_pixmap = QPixmap(self.size())
        self.chached_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(self.chached_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(Qt.PenStyle.NoPen)

        base_color = QColor(self.pixel_color)
        h_val, s_val, v_val, _ = base_color.getHsv()

        cols = math.ceil(self.width() / self.pixel_size)
        rows = math.ceil(self.height() / self.pixel_size)

        border_color = QColor("#686c75")

        for row in range(rows):
            row_factor = row / max(1, rows - 1)
            for col in range(cols):
                if not self.is_inside_bounds(col, row, cols, rows):
                    continue

                bx = col * self.pixel_size
                by = row * self.pixel_size

                is_border = (
                    not self.is_inside_bounds(col - 1, row, cols, rows) or
                    not self.is_inside_bounds(col + 1, row, cols, rows) or
                    not self.is_inside_bounds(col, row - 1, cols, rows) or
                    not self.is_inside_bounds(col, row + 1, cols, rows)
                )

                if is_border:
                    final_color = border_color
                else:
                    grad_v = int(v_val * (1.6 - row_factor * 1.1))
                    final_v = max(0, min(255, grad_v))
                    grad_s = int(s_val * (0.8 + row_factor * 0.5))
                    final_s = max(0, min(255, grad_s))
                    final_color = QColor.fromHsv(h_val, final_s, final_v)
                    final_color.setAlpha(200)
                painter.setBrush(final_color)
                painter.drawRect(bx, by, self.pixel_size, self.pixel_size)
        painter.end()

    def set_resizable(self, resizable: bool):
        policy = QSizePolicy.Policy.Preferred if resizable else QSizePolicy.Policy.Fixed
        self.setSizePolicy(policy, policy)
        self.updateGeometry()

    def paintEvent(self, event):
        """
        Стандартная функция PySide6
        Фукнция для отрисовки меню платформы
        """
        if self.chached_pixmap.isNull():
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.chached_pixmap)
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.generate_pixels()

    def _auto_align(self):
        if self.parentWidget() and self.parentWidget().layout():
            self.parentWidget().layout().setAlignment(self, Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._auto_align)