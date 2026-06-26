from PySide6.QtWidgets import QSlider
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QTimer

class PixelSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.pixel_size = 4
        self.setFixedSize(220, 20)

    def map_value_to_x(self):
        ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        return int(ratio * (self.width() - 8))

    def update_value(self, x):
        ratio = x / self.width()
        val = self.minimum() + ratio * (self.maximum() - self.minimum())
        self.setValue(int(val))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        painter.setBrush(QColor("#222222"))
        painter.setPen(QColor("#686c75"))
        painter.drawRect(0, 8, self.width(), 4)

        handle_pos = self.map_value_to_x()
        painter.setBrush(QColor("#ffffff"))
        painter.drawRect(handle_pos, 0, 8, 20)

    def mousePressEvent(self, event):
        self.update_value(event.position().x())

    def mouseMoveEvent(self, event):
        self.update_value(event.position().x())

    def _auto_align(self):
        if self.parentWidget() and self.parentWidget().layout():
            self.parentWidget().layout().setAlignment(self, Qt.AlignmentFlag.AlignHCenter)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._auto_align)