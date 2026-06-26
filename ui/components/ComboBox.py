import math
from PySide6.QtWidgets import (
    QComboBox, QStyledItemDelegate,
    QStyle, QFrame, QListView
)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import QRect, Qt, QTimer

from Configuration import MAIN_FONT
from ui.components.TextLineWidget import load_font

class PixelListView(QListView):
    """
    Класс
    """
    def __init__(self, parent=None, pixel_size=4, r=2):
        super().__init__(parent)
        self.pixel_size = pixel_size
        self.r = r

        self.setFrameShape(QListView.Shape.NoFrame)
        self.setFrameShadow(QListView.Shadow.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        w = self.viewport().width()
        h = self.viewport().height()
        cols = math.ceil(w / self.pixel_size)
        rows = math.ceil(h / self.pixel_size)

        painter.setPen(Qt.PenStyle.NoPen)
        bg_color = QColor(35, 35, 35)

        for row in range(rows):
            for col in range(cols):
                is_top_left = (col + row) < self.r
                is_top_right = ((cols - 1 - col) + row) < self.r
                is_bottom_left = (col + (rows - 1 - row)) < self.r
                is_bottom_right = ((cols - 1 - col) + (rows - 1 - row)) < self.r
                
                if is_top_left or is_top_right or is_bottom_left or is_bottom_right:
                    continue

                painter.setBrush(bg_color)
                painter.drawRect(col * self.pixel_size,
                                 row * self.pixel_size,
                                 self.pixel_size, self.pixel_size)
        painter.end()
        super().paintEvent(event)

class PixelComboDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, pixel_size=4, r=2):
        super().__init__(parent)
        self.pixel_size = pixel_size
        self.r = r

    def paint(self, painter : QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        rect = option.rect

        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_mouse_over = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected or is_mouse_over:
            bg_color = QColor(70, 73, 80)

            model = index.model()
            row_index = index.row()
            total_rows = model.rowCount() if model else 1

            cols = math.ceil(rect.width() / self.pixel_size)
            rows = math.ceil(rect.height() / self.pixel_size)

            painter.setPen(Qt.PenStyle.NoPen)
            for row in range(rows):
                for col in range(cols):
                    is_corner = False
                    if row_index == 0:
                        if (col + row) < self.r:
                            is_corner = True
                        if ((cols - 1 - col) + row) < self.r:
                            is_corner = True
                    if row_index == total_rows - 1:
                        if (col + (rows - 1 - row)) < self.r:
                            is_corner = True
                        if ((cols - 1 - col) + (rows - 1 - row)) < self.r:
                            is_corner = True
                    if is_corner:
                        continue
                    painter.setBrush(bg_color)
                    painter.drawRect(rect.x() + col * self.pixel_size,
                                     rect.y() + row * self.pixel_size,
                                     self.pixel_size, self.pixel_size)

        painter.setPen(Qt.GlobalColor.white)
        if option.widget:
            painter.setFont(option.widget.font())
        else:
            painter.setFont(option.font)

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(32)
        return size

class PixelComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixel_size = 4
        self.r = 2
        self.setFixedSize(220, 32)
        self.setFont(QFont(load_font(MAIN_FONT), 10))

        view = PixelListView(self, self.pixel_size, self.r)
        
        view.setFont(self.font())
        self.setView(view)
        view.setUniformItemSizes(True)
        view.setItemDelegate(PixelComboDelegate(view, self.pixel_size, self.r))
    
        container = view.parentWidget()
        if container:
            container.setFrameShape(QFrame.Shape.NoFrame)
            container.setFrameShadow(QFrame.Shadow.Plain)
            container.setLineWidth(0)
            container.setMidLineWidth(0)
            
            container.setContentsMargins(0, 0, 0, 0)
            if container.layout():
                container.layout().setContentsMargins(0, 0, 0, 0)
                container.layout().setSpacing(0)
                
            container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def get_rounded_corener(self, col, row, r):
        """
        Функция для 'квадрагления' кнопки
        """
        cols = math.ceil(self.width() / self.pixel_size)
        rows = math.ceil(self.height() / self.pixel_size)
        is_top_left = (col + row) < r
        is_top_right = ((cols - 1 - col) + row) < r
        is_bottom_left = (col + (rows - 1 - row)) < r
        is_bottom_right = ((cols - 1 - col) + (rows - 1 - row)) < r
        return is_top_left or is_top_right or is_bottom_left or is_bottom_right
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        cols = math.ceil(self.width() / self.pixel_size)
        rows = math.ceil(self.height() / self.pixel_size)

        painter.setPen(Qt.PenStyle.NoPen)
        for row in range(rows):
            factor = row / max(1, rows - 1)
            value = int(50 - factor * 20)
            color = QColor(value, value, value)
            for col in range(cols):
                if self.get_rounded_corener(col, row, self.r):
                    continue
                painter.setBrush(color)
                painter.drawRect(col * self.pixel_size, row * self.pixel_size, self.pixel_size, self.pixel_size)
        
        sep_x = self.width() - 32
        painter.setBrush(QColor(80, 80, 80))
        painter.drawRect(sep_x, 4, 4, self.height() - 8)

        # Текст
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(self.font())
        text_rect = QRect(0, 0, sep_x, self.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.currentText())
        
        # Стрелочки
        arrow_x = self.width() - 18
        arrow_y = self.height() // 2 - 2
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(arrow_x, arrow_y, 4, 4)
        painter.drawRect(arrow_x - 4, arrow_y - 4, 12, 4)

    def _auto_align(self):
        if self.parentWidget() and self.parentWidget().layout():
            self.parentWidget().layout().setAlignment(self, Qt.AlignmentFlag.AlignHCenter)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._auto_align)

    def showPopup(self):
        super().showPopup()
        popup_window = self.view().window()
        if popup_window and popup_window != self:
            popup_window.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
            popup_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            
            popup_window.show()