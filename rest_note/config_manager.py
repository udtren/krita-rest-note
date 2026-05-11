import json
import os

DEFAULT_CONFIG = {
    "work_break_enabled": True,  
    "work_minutes": 50,
    "break_minutes": 10,
    "micro_break_enabled": True,
    "micro_break_interval_minutes": 20,
    "micro_break_duration_seconds": 20,
    "micro_skip_threshold_seconds": 180,  # 大休憩が3分以内ならスキップ
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
            self._data = dict(DEFAULT_CONFIG)
            self._data.update(loaded)
        except (json.JSONDecodeError, OSError):
            self._data = dict(DEFAULT_CONFIG)
    
    def save(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
    
    # ── Big break (50/10) ──
    @property
    def work_break_enabled(self):
        return bool(self._data.get("work_break_enabled", True))
    
    @work_break_enabled.setter
    def work_break_enabled(self, value):
        self._data["work_break_enabled"] = bool(value)
    
    @property
    def work_minutes(self):
        return int(self._data.get("work_minutes", 50))
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
    
    # ── 20-20-20 micro break ──
    @property
    def micro_enabled(self):
        return bool(self._data.get("micro_break_enabled", True))
    
    @micro_enabled.setter
    def micro_enabled(self, value):
        self._data["micro_break_enabled"] = bool(value)
    
    @property
    def micro_interval_minutes(self):
        return int(self._data.get("micro_break_interval_minutes", 20))
    
    @micro_interval_minutes.setter
    def micro_interval_minutes(self, value):
        self._data["micro_break_interval_minutes"] = int(value)
    
    @property
    def micro_interval_seconds(self):
        return self.micro_interval_minutes * 60
    
    @property
    def micro_duration_seconds(self):
        return int(self._data.get("micro_break_duration_seconds", 20))
    
    @micro_duration_seconds.setter
    def micro_duration_seconds(self, value):
        self._data["micro_break_duration_seconds"] = int(value)
    
    @property
    def micro_skip_threshold(self):
        return int(self._data.get("micro_skip_threshold_seconds", 180))
    
    @micro_skip_threshold.setter
    def micro_skip_threshold(self, value):
        self._data["micro_skip_threshold_seconds"] = int(value)
