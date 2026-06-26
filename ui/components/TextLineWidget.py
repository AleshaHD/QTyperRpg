import os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QFont, QColor, QPainter, QFontDatabase,
    QFontMetrics, QPainterPath, QPen
)
from PySide6.QtCore import Qt, QRect, QSize

from Configuration import *

def load_font(path):
    full_path = get_font_path(path)

    if not os.path.exists(full_path):
        print(f"Не найден шрифт: {full_path}")
        return "Arial"
    font_id = QFontDatabase.addApplicationFont(full_path)
    if font_id == -1:
        return "Arial"
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
        return font_families[0]
    return "Arial"

class TextLineWidget(QWidget):
    """
    Класс для отрисовки текста на экране
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self.index = 0
        self.setFixedHeight(80)
        self.setFont(QFont(load_font(MAIN_FONT), 26))

    def set_text_state(self, text, index):
        self.text = text
        self.index = index
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)
        painter.setFont(self.font())

        metrics = QFontMetrics(self.font())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        actual_width = min(1600, self.width() - 32)
        x_offset = (self.width() - actual_width) // 2

        panel_rect = QRect(x_offset, 4, actual_width, self.height() - 8)
        center_x = panel_rect.x() + panel_rect.width() // 2
        baseline_y = panel_rect.center().y() + metrics.ascent() // 2 - 1

        clip_path = QPainterPath()
        clip_path.addRoundedRect(panel_rect, 12, 12)

        painter.save()
        painter.setClipPath(clip_path)

        left_rect = QRect(panel_rect)
        left_rect.setRight(center_x)
        painter.fillRect(left_rect, QColor(210, 210, 210))

        right_rect = QRect(panel_rect)
        right_rect.setLeft(center_x)
        painter.fillRect(right_rect, QColor(255, 255, 255))

        painter.restore()

        painter.setPen(QPen(QColor(170, 170, 170), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(panel_rect, 12, 12)

        painter.setPen(QPen(QColor(130, 130, 130), 2))
        painter.drawLine(center_x, panel_rect.top() + 4, center_x, panel_rect.bottom() - 4)
        
        # Текст
        text = self.text
        index = self.index

        if not text:
            painter.end()
            return

        visible_before = 35
        visible_after = 55
        start = max(0, index - visible_before)
        end = min(len(text), index + visible_after)

        visible_text = text[start:end]
        local_index = index - start

        typed = visible_text[:local_index]
        current = visible_text[local_index] if local_index < len(visible_text) else ""
        remaining = visible_text[local_index + 1:] if local_index < len(visible_text) else ""

        typed_w = metrics.horizontalAdvance(typed)
        current_w = metrics.horizontalAdvance(current if current != " " else " ")

        current_x = center_x + 2
        typed_x = current_x - typed_w
        remaining_x = current_x + current_w

        # Отступ текста
        content_rect = panel_rect.adjusted(8, 0, -8, 0)
        painter.save()
        painter.setClipRect(content_rect)

        # Текст который уже набрали
        painter.setPen(QColor(130, 130, 130))
        painter.drawText(typed_x, baseline_y, typed)

        # Текущий символ
        painter.setPen(QColor(0, 0, 0))
        if current:
            # Выделение пробела пробела
            if current != " ":
                painter.drawText(current_x, baseline_y, current)
        
        painter.setPen(QColor(35, 35, 35))
        painter.drawText(remaining_x, baseline_y, remaining)

        painter.restore()
        painter.end()

class PixelTextWidget(QWidget):
    """
    Кастомный виджет для отрисовки текста с эффектами (замена QLabel).
    Поддерживает кастомный шрифт, тени, обводку и выравнивание.
    """
    def __init__(self, text="", font_size=16, font_path=None, parent=None):
        super().__init__(parent)
        self._calculated_size = None
        self.text = text
        self.font_size = font_size

        font_family = load_font(font_path) if font_path else "Arial"
        self.setFont(QFont(font_family, self.font_size))

        self.text_color = QColor(255, 255, 255)
        self.alignment = Qt.AlignmentFlag.AlignCenter

        self.has_shadow = False
        self.shadow_color = QColor(0, 0, 0, 180)
        self.shadow_offset_x = 3
        self.shadow_offset_y = 3

        self.has_outline = False
        self.outline_color = QColor(0, 0, 0)
        self.outline_thickness = 2

        self.update_geometry_size()

    def set_text(self, text):
        if self.text == text: return
        self.text = text
        self.update_geometry_size()
        self.adjustSize()
        self.update()

    def set_effects(self, color=QColor(255, 255, 255), alignment=Qt.AlignmentFlag.AlignCenter,
                    shadow=False, outline=False, shadow_color=QColor(0, 0, 0, 180), outline_color=QColor(0, 0, 0)):
        """
        Метод для быстрой конфигурации стиля текста
        """
        self.text_color = color
        self.alignment = alignment
        self.has_shadow = shadow
        self.has_outline = outline
        self.shadow_color = shadow_color
        self.outline_color = outline_color
        self.update_geometry_size()
        self.update()

    def update_geometry_size(self):
        metrics = QFontMetrics(self.font())

        if self.text:
            rect = metrics.boundingRect(self.text)
            w = rect.width()
            h = rect.height()
        else:
            w = 10
            h = 10

        if self.has_outline:
            w += self.outline_thickness * 2
            h += self.outline_thickness * 2

        if self.has_shadow:
            w += self.shadow_offset_x
            h += self.shadow_offset_y

        w += 10
        h += 10

        self._calculated_size = QSize(w, h)

        self.setMinimumSize(self._calculated_size)
        self.updateGeometry()

    def setText(self, text):
        self.set_text(text)

    def sizeHint(self):
        return self._calculated_size
    
    def minimumSizeHint(self):
        return self._calculated_size
    
    def paintEvent(self, event):
        if not self.text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)
        painter.setFont(self.font())

        rect = self.rect()
        metrics = QFontMetrics(self.font())

        w = metrics.horizontalAdvance(self.text)
        h = metrics.height()

        x = (rect.width() - w) // 2
        y = (rect.height() - h) // 2 + metrics.ascent()

        # Эффект обводки - Outline
        if self.has_outline:
            path = QPainterPath()
            path.addText(x, y, self.font(), self.text)
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

            pen = QPen(self.outline_color, self.outline_thickness * 2)
            pen.setStyle(Qt.PenStyle.SolidLine)
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)

            painter.setPen(pen)
            painter.drawPath(path)
            painter.restore()

        # Эффект тени - Shadow
        elif self.has_shadow:
            painter.setPen(self.shadow_color)
            shadow_rect = rect.translated(self.shadow_offset_x, self.shadow_offset_y)
            painter.drawText(shadow_rect, self.alignment, self.text)

        # Основной текст - рисуется поверх тени/обводки
        painter.setPen(self.text_color)
        painter.drawText(rect, self.alignment, self.text)