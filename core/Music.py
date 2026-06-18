import pygame

class MusicPlayer:
    """
    Класс для музыки
    """
    def __init__(self, volume=100):
        # Инициализируем микшер, если он еще не инициализирован
        self.mixer = pygame.mixer
        if not self.mixer.get_init():
            self.mixer.init()

        self.current_track = None
        self.set_volume(volume)

    def play_track(self, file_path):
        # Если трек уже играет, не перезапускаем его
        if self.current_track == file_path and self.mixer.music.get_busy():
            return

        if self.current_track == file_path:
            self.mixer.music.unpause()
            return

        self.mixer.music.load(file_path)
        self.mixer.music.play(loops=-1)
        self.current_track = file_path

    def stop(self):
        self.mixer.music.stop()
        self.current_track = None

    def pause(self):
        self.mixer.music.pause()

    def resume(self):
        self.mixer.music.unpause()

    def set_volume(self, value):
        self.mixer.music.set_volume(float(value) / 100.0)

    # def play(self):
    #     self.mixer.music.play()

class SoundPlayer:
    def __init__(self, volume=100):
        self.mixer = pygame.mixer
        self.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        self.sounds = {}
        self.volume = float(volume) / 100.0

    def add_sound(self, name, file_path):
        sound = self.mixer.Sound(file_path)
        sound.set_volume(self.volume)
        self.sounds[name] = sound

    def set_volume(self, value):
        self.volume = float(value) / 100.0
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()