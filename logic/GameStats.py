import time

class GameStats:
    """
    Класс игровой статистики
    """
    def __init__(self):
        # Текст
        self.current_text_index = 0
        self.target_text = ""
        self.input_text = ""
        # Статистика
        self.total_attemts = 0
        self.wrong_attemts = 0
        self.progress_bar = 0.0
        self.timer = 0.0
        self.hits = []
        # Финальная статистика
        self.final_wpm = 0.0
        self.final_accuracy = 0.0
        self.final_progress_bar = 0.0
        self.final_time = 0.0
        # Время
        self.is_finished = False
        self.elapsed_time = 0.0
        self.start_time = None
        self.pause_start_time = None
        self.total_pause_time = 0.0

    def reset(self, new_text):
        """
        Функция сброса всех показателей
        """
        self.target_text = new_text
        self.current_text_index = 0
        self.total_attemts = 0
        self.wrong_attemts = 0
        self.progress_bar = 0.0
        self.hits = []
        self.start_time = None
        self.pause_start_time = None
        self.total_pause_time = 0.0
        self.is_finished = False
        self.elapsed_time = 0.0
    def get_wpm(self):
        """
        Функция для получения количества набора символов в минуту
        """
        if self.start_time is None:
            return 0.0
        total_time = time.time() - self.start_time - self.total_pause_time
        if total_time > 0.1  and self.current_text_index > 0:
            return round((self.current_text_index / 5) / (total_time / 60))
        return 0.0
    def get_accuracy(self):
        """
        Функция для получения точности набора символов
        """
        if not self.hits:
            return 0.0
        return round((sum(self.hits) / len(self.hits)) * 100, 1)
    def get_progress_bar(self):
        """
        Функция для получения стадии прогресса на уровне
        """
        if len(self.target_text) > 0:
            return round((self.current_text_index / len(self.target_text)) * 100, 1)
        return 0.0
    def get_elapsed(self):
        """
        Функция для получения времени
        """
        if self.start_time is None:
            return 0.0
        if self.is_finished:
            return self.elapsed_time
        return max(0.0, time.time() - self.start_time - self.total_pause_time)
    def get_timer(self):
        """
        Функция для получения финального времени
        """
        elapsed = int(self.get_elapsed())
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
    def finish_timer(self):
        if self.start_time is not None:
            self.elapsed_time = self.get_elapsed()
            self.is_finished = True
    def format_time(self, seconds):
        seconds = int(seconds)
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"
    def save_final_stats(self):
        """
        Функция для сохранения финальной статистики
        """
        self.final_wpm = self.get_wpm()
        self.final_accuracy = self.get_accuracy()
        self.final_progress_bar = self.get_progress_bar()
        self.final_time = self.elapsed_time
    def start_pause(self):
        if self.pause_start_time is None:
            self.pause_start_time = time.time()
    def end_pause(self):
        if self.pause_start_time is not None:
            self.total_pause_time += time.time() - self.pause_start_time
            self.pause_start_time = None
