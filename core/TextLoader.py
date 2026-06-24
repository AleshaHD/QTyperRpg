import os, random

from Configuration import TEST_TEXT, Difficult

class TextLoader:
    """
    Класс для загрузки, изменения и выдавания текста из файлов
    """
    def __init__(self, obj):
        self.game = obj
        self.__base_path = "assets/texts"
        self.clean_text = True
        self.to_lower = False

    def _open_file(self, file_name):
        """
        Функция открытия файлов из папки
        """
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                file = f.read()
        except UnicodeDecodeError:
            with open(file_name, 'r', encoding='cp1251') as f:
                file = f.read()
        if self.to_lower:
            file = file.lower()
        if self.clean_text:
            chars_to_remove = ['.', ',', '!', '?', '-', '(', ')', '[', ']', '{', '}']
            for char in chars_to_remove:
                file = file.replace(char, '')
        return ' '.join(file.split())

    def get_random_text(self, difficult):
        """
        Функция рандомного выбора файла с текстом
        """
        if TEST_TEXT:
            return self._open_file("assets/texts/test.txt")

        else:
            current_lang = self.game.current_lang_layout 
            folder_path = os.path.join(self.__base_path, current_lang)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                return f"Папка {folder_path} создана, добавьте в нее файлы .txt"

            files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        
            if not files:
                return "Файлы с текстом не найдены"
            
            if difficult == Difficult.EASY:
                self.clean_text = True
                self.to_lower = True
            elif difficult == Difficult.NORMAL:
                self.clean_text = True
                self.to_lower = False
            elif difficult == Difficult.HARD:
                self.clean_text = False
                self.to_lower = False
            
            target_file = random.choice(files)
            full_path = os.path.join(folder_path, target_file)

            print(f"Текст из файла: {target_file}")
            return self._open_file(full_path)