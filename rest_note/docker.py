from krita import DockWidget
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics

from .config_manager import ConfigManager
from .config_dialog import ConfigDialog
from .overlay import CalmBreakOverlay
from .micro_toast import MicroBreakToast


class RestNoteDocker(DockWidget):
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_BREAK = "break"
    STATE_MICRO_BREAK = "micro_break"
    
    # Font scaling
    TIME_MIN_PT = 14
    TIME_MAX_PT = 96
    STATUS_MIN_PT = 8
    STATUS_MAX_PT = 24
    SUB_MIN_PT = 8
    SUB_MAX_PT = 18
    STATUS_RATIO = 0.28
    SUB_RATIO = 0.22
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rest Note")
        
        self.config = ConfigManager()
        self.state = self.STATE_RUNNING
        
        # Big break countdown (seconds)
        self.remaining = self.config.work_seconds
        # Micro break countdown (seconds until next eye break)
        self.micro_remaining = self.config.micro_interval_seconds
        
        self.overlay = None        # CalmBreakOverlay instance
        self.micro_toast = None    # MicroBreakToast instance
        
        # 1-second tick for both timers
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self._on_tick)
        self.tick_timer.start(1000)
        
        self._build_ui()
        self._refresh_display()
    
    # ── UI ──
    def _build_ui(self):
        root = QWidget()
        root.resizeEvent = self._on_root_resize
        self._root = root
        
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Status
        self.status_label = QLabel("WORKING")
        self.status_label.setStyleSheet(
            "color: #b8b8b8; letter-spacing: 2px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Big time
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("color: #e6dcc8;")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Sub-info: next eye break
        self.sub_label = QLabel("Next eye break in 00:00")
        self.sub_label.setStyleSheet("color: rgba(184,184,184,180);")
        self.sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sub_label)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,30);")
        layout.addWidget(sep)
        
        row1 = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        row1.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        row1.addWidget(self.reset_btn)
        layout.addLayout(row1)
        
        self.config_btn = QPushButton("Config…")
        self.config_btn.clicked.connect(self._on_config_clicked)
        layout.addWidget(self.config_btn)
        
        layout.addStretch(1)
        self.setWidget(root)
        
        self._update_font_sizes(root.width(), root.height())
    
    # ── Dynamic font sizing ──
    def _on_root_resize(self, event):
        QWidget.resizeEvent(self._root, event)
        size = event.size()
        self._update_font_sizes(size.width(), size.height())
    
    def _update_font_sizes(self, width, height):
        from_width = width / 5.5
        from_height = height / 5.5
        time_pt = int(min(from_width, from_height))
        time_pt = max(self.TIME_MIN_PT, min(self.TIME_MAX_PT, time_pt))
        
        status_pt = int(time_pt * self.STATUS_RATIO)
        status_pt = max(self.STATUS_MIN_PT, min(self.STATUS_MAX_PT, status_pt))
        
        sub_pt = int(time_pt * self.SUB_RATIO)
        sub_pt = max(self.SUB_MIN_PT, min(self.SUB_MAX_PT, sub_pt))
        
        time_font = QFont()
        time_font.setPointSize(time_pt)
        time_font.setWeight(QFont.Light)
        self.time_label.setFont(time_font)
        self.time_label.setMinimumHeight(QFontMetrics(time_font).height() + 6)
        
        status_font = QFont()
        status_font.setPointSize(status_pt)
        self.status_label.setFont(status_font)
        self.status_label.setMinimumHeight(QFontMetrics(status_font).height() + 2)
        
        sub_font = QFont()
        sub_font.setPointSize(sub_pt)
        self.sub_label.setFont(sub_font)
        self.sub_label.setMinimumHeight(QFontMetrics(sub_font).height() + 2)
    
    # ── Tick: heart of the integration ──
    def _on_tick(self):
        if self.state == self.STATE_RUNNING:
            self.remaining -= 1
            
            # Big break trigger has top priority
            if self.remaining <= 0:
                self._start_big_break()
                self._refresh_display()
                return
            
            # Micro break (20-20-20)
            if self.config.micro_enabled:
                self.micro_remaining -= 1
                if self.micro_remaining <= 0:
                    self._maybe_trigger_micro_break()
        
        elif self.state == self.STATE_MICRO_BREAK:
            # Big break timer keeps running during a 20-second eye break.
            # The micro timer itself is handled by the toast widget.
            self.remaining -= 1
            if self.remaining <= 0:
                # Cancel micro toast and go straight to big break
                if self.micro_toast is not None:
                    self.micro_toast.cancel()
                    self.micro_toast = None
                self._start_big_break()
        
        # PAUSED, BREAK: both timers frozen
        
        self._refresh_display()
    
    # ── Micro break logic ──
    def _maybe_trigger_micro_break(self):
        """20分タイマーが0になった時に呼ばれる。大休憩が近ければスキップ。"""
        # 大休憩との近接スキップ
        if self.remaining <= self.config.micro_skip_threshold:
            self.micro_remaining = self.config.micro_interval_seconds
            return
        
        self.state = self.STATE_MICRO_BREAK
        self.micro_toast = MicroBreakToast(
            duration_seconds=self.config.micro_duration_seconds
        )
        self.micro_toast.finished.connect(self._end_micro_break)
        self.micro_toast.show()
    
    def _end_micro_break(self):
        self.micro_toast = None
        self.micro_remaining = self.config.micro_interval_seconds
        # 大休憩に飛んでない場合のみRUNNINGに戻す
        if self.state == self.STATE_MICRO_BREAK:
            self.state = self.STATE_RUNNING
        self._refresh_display()
    
    # ── Big break logic (方針②: 大休憩中はmicroを停止) ──
    def _start_big_break(self):
        # Cancel any in-flight micro toast
        if self.micro_toast is not None:
            self.micro_toast.cancel()
            self.micro_toast = None
        # Reset micro counter for after the big break
        self.micro_remaining = self.config.micro_interval_seconds
        
        self.state = self.STATE_BREAK
        self.remaining = 0
        
        self.overlay = CalmBreakOverlay(
            break_seconds=self.config.break_seconds
        )
        self.overlay.breakFinished.connect(self._end_big_break)
        self.overlay.show()
    
    def _end_big_break(self):
        self.overlay = None
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self.micro_remaining = self.config.micro_interval_seconds
        self._refresh_display()
    
    # ── Display ──
    def _refresh_display(self):
        m, s = divmod(max(0, self.remaining), 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")
        
        # Status
        if self.state == self.STATE_RUNNING:
            self.status_label.setText("WORKING")
            self.pause_btn.setText("Pause")
            self.pause_btn.setEnabled(True)
        elif self.state == self.STATE_PAUSED:
            self.status_label.setText("PAUSED")
            self.pause_btn.setText("Resume")
            self.pause_btn.setEnabled(True)
        elif self.state == self.STATE_BREAK:
            self.status_label.setText("ON BREAK")
            self.pause_btn.setEnabled(False)
        elif self.state == self.STATE_MICRO_BREAK:
            self.status_label.setText("EYE BREAK")
            self.pause_btn.setEnabled(True)
        
        # Sub-label: next eye break info
        if not self.config.micro_enabled:
            self.sub_label.setText("Eye break: disabled")
        elif self.state == self.STATE_BREAK:
            self.sub_label.setText("—")
        elif self.state == self.STATE_MICRO_BREAK:
            self.sub_label.setText("Look ~6m away")
        else:
            mm, ss = divmod(max(0, self.micro_remaining), 60)
            self.sub_label.setText(f"Next eye break in {mm:02d}:{ss:02d}")
    
    # ── Buttons ──
    def _on_pause_clicked(self):
        if self.state == self.STATE_RUNNING:
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.state = self.STATE_RUNNING
        elif self.state == self.STATE_MICRO_BREAK:
            # Pause during micro: cancel toast, freeze timers
            if self.micro_toast is not None:
                self.micro_toast.cancel()
                self.micro_toast = None
            self.state = self.STATE_PAUSED
        self._refresh_display()
    
    def _on_reset_clicked(self):
        # Close anything active
        if self.overlay is not None:
            self.overlay.close()
            self.overlay = None
        if self.micro_toast is not None:
            self.micro_toast.cancel()
            self.micro_toast = None
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self.micro_remaining = self.config.micro_interval_seconds
        self._refresh_display()
    
    def _on_config_clicked(self):
        dialog = ConfigDialog(self.config, parent=self.widget())
        if dialog.exec_():
            dialog.apply_to_config()
            # 進行中の作業はなるべく邪魔しない方針
            if self.state == self.STATE_RUNNING:
                if self.remaining > self.config.work_seconds:
                    self.remaining = self.config.work_seconds
                if self.micro_remaining > self.config.micro_interval_seconds:
                    self.micro_remaining = self.config.micro_interval_seconds
            else:
                self.remaining = self.config.work_seconds
                self.micro_remaining = self.config.micro_interval_seconds
            self._refresh_display()
    
    def canvasChanged(self, canvas):
        pass
