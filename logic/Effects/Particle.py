import random

class Particle:
    """
    Класс для создания частиц на заднем фоне
    """
    def __init__(self, w, h):
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.speed = random.uniform(0.2, 1.0)
        self.size = random.randint(2, 5)
        self.alpha = random.randint(180, 230)