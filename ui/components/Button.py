import random, time, math
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCore import QPoint, Qt, QTimer

from Configuration import MAIN_FONT
from ui.components.TextLineWidget import load_font

class PixelButton(QPushButton):
    """
    Класс для создания кастомной кнопки
    """
    def __init__(self, text, parent=None, color_hex="#8b0000"):
        super().__init__(text, parent)
        self.pixel_color = QColor(color_hex)
        self.pixels = []
        # Размер пикселей
        self.pixel_size = 5
        self.last_time = time.time()
        self.r = 2

        self._click_debounce_time = 0.0

        self.setMouseTracking(True)
        self.cursor_pos = QPoint(0, 0)
        self.is_hovered = False

        self.setFixedSize(220, 48)
        self.setFont(QFont(load_font(MAIN_FONT), 12, QFont.Weight.Bold))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_pixels)
        self.timer.start(16)

    def animate_pixels(self):
        """
        Функция для анимирования кнопки
        """
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        dt = min(dt, 0.016)

        is_hovered = self.is_hovered
        rect = self.rect()
        is_cursor_inside = rect.adjusted(-2, -2, 2, 2).contains(self.cursor_pos)
        is_swarm_active = is_hovered and is_cursor_inside

        for p in self.pixels:
            if not p['is_follower']:
                if is_swarm_active:
                    if p['delay_timer'] > 0:
                        p['delay_timer'] -= dt
                    else:
                        p['progress'] = min(1.0, p['progress'] + dt * 3.5)

                else:
                    p['progress'] = max(0.0, p['progress'] - dt * 4.0)
                    p['delay_timer'] = p['max_delay']
                t = p['progress']
                p['cx'] = p['bx'] + p['tx'] * t
                p['cy'] = p['by'] + p['ty'] * t
                p['alpha'] = int(255 * (1.0 - t))
            else:
                if is_swarm_active:
                    target_x = self.cursor_pos.x()
                    target_y = self.cursor_pos.y()
                    
                    # Тянутся к мыши
                    p['cx'] += (target_x + p['noise_x'] - p['cx']) * p['speed'] * dt
                    p['cy'] += (target_y + p['noise_y'] - p['cy']) * p['speed'] * dt

                    # Затухание от расстояния до базы
                    dx_base = p['cx'] - p['bx']
                    dy_base = p['cy'] - p['by']
                    dist_base = math.hypot(dx_base, dy_base)
                    max_dist = 50
                    p['alpha'] = int(max(0, 255 * (1.0 - (dist_base / max_dist))))

                else:
                    # Возврат домой, если мышь ушла
                    dx = p['bx'] - p['cx']
                    dy = p['by'] - p['cy']
                    dist_to_base = math.hypot(dx, dy)
                    if dist_to_base < 1.0:
                        p['cx'], p['cy'] = p['bx'], p['by']
                        p['alpha'] = 255
                    else:
                        p['cx'] += dx * 12.0 * dt
                        p['cy'] += dy * 12.0 * dt
                        p['alpha'] = int(min(255, p['alpha'] + 500 * dt))
        self.update()

    def generate_pixels(self):
        """
        Функция для создания пикселей для кнопки
        """
        self.pixels.clear()

        base_color = QColor(self.pixel_color)
        h_val, s_val, v_val, _ = base_color.getHsv()
        follower_chance = 0.6

        cols = math.ceil(self.width() / self.pixel_size)
        rows = math.ceil(self.height() / self.pixel_size)
        for row in range(rows):
            row_factor = row / max(1, rows - 1)
            for col in range(cols):

                # Скругление
                if self.get_rounded_corener(col, row, self.r):
                    continue

                bx = col * self.pixel_size
                by = row * self.pixel_size
                # Разлет частиц
                tx = (random.random() - 0.5) * 30
                ty = (random.random() - 0.5) * 30
                delay = random.uniform(0, 0.4)

                # Разброс градиента
                grad_v = int(v_val * (1.3 - row_factor * 0.67))
                noise = random.randint(-14, 14)
                final_v = max(0, min(255, grad_v + noise))
                final_s = max(0, min(255, int(s_val * (1.0 + row_factor * 0.15))))
                current_pixel_color = QColor.fromHsv(h_val, final_s, final_v)
                
                is_follower = random.random() < follower_chance
                speed = random.uniform(2.2, 5.4)
                noise_x = random.randint(-8, 8)
                noise_y = random.randint(-8, 8)

                self.pixels.append({
                    'bx': bx, 'by': by,
                    'tx': tx, 'ty': ty,
                    'cx': bx, 'cy': by,
                    'is_follower': is_follower,
                    'speed': speed,
                    'noise_x': noise_x,
                    'noise_y': noise_y,
                    'alpha': 255,
                    'delay_timer': delay,
                    'max_delay': delay,
                    'progress': 0.0,
                    'color': current_pixel_color
                })
    
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
        """
        Стандартная функция PySide6
        Фукнция для отрисовки кнопки
        """
        if not self.pixels:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        is_pressed = self.isDown()
        offset_y = 4 if is_pressed else 0

        # То что под слоем пикселей после того как навелся
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#222222"))

        cols = math.ceil(self.width() / self.pixel_size)
        rows = math.ceil(self.height() / self.pixel_size)

        for row in range(rows):
            for col in range(cols):
                # Скругление
                if self.get_rounded_corener(col, row, self.r):
                    continue
                bx = col * self.pixel_size
                by = row * self.pixel_size
                painter.drawRect(bx, by + offset_y, self.pixel_size, self.pixel_size)
        for p in self.pixels:
            if p['alpha'] > 0:
                color = QColor(p['color'])
                jitter_x = 0
                jitter_y = 0
                if is_pressed:
                    color = color.lighter(240)
                    jitter_x = random.randint(-2, 2)
                    jitter_y = random.randint(-2, 2)
                color.setAlpha(p['alpha'])
                painter.setBrush(color)
                final_x = int(p['cx']) + jitter_x
                final_y = int(p['cy']) + jitter_y + offset_y
                painter.drawRect(final_x, final_y, self.pixel_size, self.pixel_size)
        if is_pressed:
            painter.setPen(QColor("#ffffff"))
            text_jitter_x = random.randint(-1, 1)
            text_jitter_y = random.randint(-1, 1)
            text_rect = self.rect().adjusted(text_jitter_x, offset_y + text_jitter_y, text_jitter_x, offset_y + text_jitter_y)
        else:
            painter.setPen(QColor("#ffffff"))
            text_rect = self.rect().adjusted(0, 0, 0, 0)
        painter.setFont(self.font())
        text_rect = self.rect().adjusted(0, offset_y, 0, offset_y)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.generate_pixels()

    def enterEvent(self, event):
        self.is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        current_time = time.time()
        if current_time - self._click_debounce_time < 0.067:
            event.ignore()
            return
        self._click_debounce_time = current_time
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update()

    def mouseMoveEvent(self, event):
        self.cursor_pos = event.pos()
        super().mouseMoveEvent(event)