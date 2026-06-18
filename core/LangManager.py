import os, csv
from PySide6.QtCore import QObject, Signal

class LangManager(QObject):
    language_changed = Signal()
    def __init__(self, path):
        super().__init__()
        self.traslation = {}
        self.languages = {}
        self.lang = "ru"
        self.load(path)

    def load(self, path):
        if not os.path.exists(path):
            return
        valid_lang_codes = {"ru", "en"} 
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                key = row['key']
                if key.startswith("lang_"):
                    code = key.split("_")[1]
                    if code in valid_lang_codes:
                        self.languages[code] = {"en": row['en'], "ru": row['ru']}
                    else:
                        self.traslation[key] = {"en": row['en'], "ru": row['ru']}
                else:
                    self.traslation[key] = {"en": row['en'], "ru": row['ru']}

    def set_lang(self, lang):
        self.lang = lang

    def get(self, key):
        return self.traslation.get(key, {}).get(self.lang, f"[{key}]")
    
    def get_list(self):
        result = []
        for code, names in self.languages.items():
            current_trans = names[self.lang]
            native_name = names[code]

            display_name = f"{current_trans} | {native_name}"
            result.append((code, display_name))
        return result
    def get_only_list(self):
        result = []
        for code, names in self.languages.items():
            display_name = names.get(self.lang)
            result.append((code, display_name))
        return result