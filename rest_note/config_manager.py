import json
import os

DEFAULT_CONFIG = {
    "work_minutes": 50,
    "break_minutes": 10,
}


class ConfigManager:
    def __init__(self):
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(plugin_dir, "config")
        self.config_path = os.path.join(self.config_dir, "main.json")
        self._data = {}
        self.load()
    
    def load(self):
        if not os.path.exists(self.config_path):
            self._data = dict(DEFAULT_CONFIG)
            self.save()
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # Merge with defaults to handle missing keys
            self._data = dict(DEFAULT_CONFIG)
            self._data.update(loaded)
        except (json.JSONDecodeError, OSError):
            self._data = dict(DEFAULT_CONFIG)
    
    def save(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
    
    @property
    def work_minutes(self):
        return int(self._data.get("work_minutes", 50))
    
    @work_minutes.setter
    def work_minutes(self, value):
        self._data["work_minutes"] = int(value)
    
    @property
    def break_minutes(self):
        return int(self._data.get("break_minutes", 10))
    
    @break_minutes.setter
    def break_minutes(self, value):
        self._data["break_minutes"] = int(value)
    
    @property
    def work_seconds(self):
        return self.work_minutes * 60
    
    @property
    def break_seconds(self):
        return self.break_minutes * 60
