import random, os
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QTimer

from logic.Effects.Particle import Particle

class BackgroundManager:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_base = os.path.abspath(os.path.join(current_dir, "../..", "assets", "images", "bg"))
        self.backgrounds = [
            os.path.join(assets_base, "battleback", "battleback1.png"),
            os.path.join(assets_base, "battleback", "battleback2.png"),
            os.path.join(assets_base, "battleback", "battleback3.png"),
            os.path.join(assets_base, "battleback", "battleback4.png"),
            os.path.join(assets_base, "battleback", "battleback5.png"),
            os.path.join(assets_base, "battleback", "battleback6.png"),
            os.path.join(assets_base, "battleback", "battleback7.png"),
            os.path.join(assets_base, "battleback", "battleback8.png"),
            os.path.join(assets_base, "battleback", "battleback9.png"),
            os.path.join(assets_base, "battleback", "battleback10.png")
        ]

    def set_random_bg(self, widget: QWidget):
        bg_path = random.choice(self.backgrounds)
        palette = widget.palette()
        pixmap = QPixmap(bg_path)
        palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(widget.size())))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

    def get_random_pixmap(self):
        return QPixmap(random.choice(self.backgrounds))

class BackgroundPage(QWidget):
    """
    Класс заднего фона
    """
    def __init__(self, obj, particles_enabled=False, use_random=False, bg_path=None, bg_color=None):
        super().__init__()
        self.game = obj
        self.bg = QPixmap(bg_path) if bg_path else None
        self.bg_color = bg_color
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.particles_enabled = particles_enabled
        self.particles = []
        self.wind_x = 0.0
        self.last_window_pos = self.game.pos()
        self.last_size = self.size()
        self.window_initialized = False

        self.bg_manager = BackgroundManager()
        if use_random:
            self.refresh_background()
        elif bg_path:
            self.bg = QPixmap(bg_path)
        else:
            self.bg = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_particles)
        self.timer.start(16)
    
    def create_particles(self):
        """
        Функция создания частиц
        """
        w = max(1, self.width())
        h = max(1, self.height())
        self.particles.clear()
        for _ in range(255):
            self.particles.append(Particle(w, h))

    def animate_particles(self):
        """
        Функция для анимирования частиц
        """
        if not self.particles_enabled:
            return
        current_size = self.last_size
        size_changed = current_size != self.last_size
        self.last_size = current_size
        if size_changed:
            delta_x = 0

        current_pos = self.game.pos()
        if not self.window_initialized:
            self.last_window_pos = current_pos
            self.window_initialized = True
            return
        delta_x = current_pos.x() - self.last_window_pos.x()
        if abs(delta_x) > 100:
            delta_x = 0
        self.last_window_pos = current_pos

        # Инерция для частиц
        self.wind_x += delta_x * 0.11
        # Затухание частиц
        self.wind_x *= 0.92

        w = self.width()
        h = self.height()
        
        for p in self.particles:
            p.y += p.speed
            p.x += self.wind_x * p.speed
            if p.y > h:
                p.y = -10
                p.x = random.randint(0, w)
            if p.x < -10:
                p.x = w + 10
            elif p.x > w + 10:
                p.x = -10
        self.update()

    def reset_particles(self):
        self.particles.clear()
        for _ in range(255):
            self.particles.append(Particle(self.width(), self.height()))

    def refresh_background(self):
        self.bg = self.bg_manager.get_random_pixmap()
        self.update()

    def get_blur(self):
        """
        Функция для размытия заднего фона
        """
        scaled = self.bg.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image = scaled.toImage()
        for _ in range(2):
            image = image.scaled(self.width() // 2, self.height() // 2, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image = image.scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return QPixmap.fromImage(image)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.bg and not self.bg.isNull():
            painter.drawPixmap(self.rect(), self.bg)
        elif self.bg_color:
            painter.fillRect(self.rect(), QColor(*self.bg_color))
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0))

        if self.particles_enabled:
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                painter.setBrush(QColor(100, 100, 120, p.alpha))
                painter.drawEllipse(int(p.x), int(p.y), p.size, p.size)
        painter.end()
        super().paintEvent(event)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.particles_enabled:
            self.create_particles()
