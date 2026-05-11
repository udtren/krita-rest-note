from krita import DockWidget
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics

from .config_manager import ConfigManager
from .config_dialog import ConfigDialog
from .overlay import CalmBreakOverlay


class RestNoteDocker(DockWidget):
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_BREAK = "break"
    
    # ── Font scaling parameters ──
    # The time label is the dominant visual element; sized against width.
    # Status label scales proportionally but smaller.
    TIME_MIN_PT = 14
    TIME_MAX_PT = 96
    STATUS_MIN_PT = 8
    STATUS_MAX_PT = 24
    # Ratio of status to time font size
    STATUS_RATIO = 0.28
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Break Enforcer")
        
        self.config = ConfigManager()
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self.overlay = None
        
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self._on_tick)
        self.tick_timer.start(1000)
        
        self._build_ui()
        self._refresh_display()
    
    # ── UI ──
    def _build_ui(self):
        root = QWidget()
        # Capture resize events on the root widget
        root.resizeEvent = self._on_root_resize
        self._root = root
        
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Status label
        self.status_label = QLabel("WORKING")
        self.status_label.setStyleSheet(
            "color: #b8b8b8; letter-spacing: 2px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Big remaining-time display
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("color: #e6dcc8;")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(255,255,255,30);")
        layout.addWidget(sep)
        
        # Buttons (will be swapped to PNG icons later)
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
        
        # Initial font sizing
        self._update_font_sizes(root.width(), root.height())
    
    # ── Dynamic font sizing ──
    def _on_root_resize(self, event):
        # Don't forget to chain to default behavior
        QWidget.resizeEvent(self._root, event)
        size = event.size()
        self._update_font_sizes(size.width(), size.height())
    
    def _update_font_sizes(self, width, height):
        """Recompute font sizes from current docker dimensions."""
        # Time label: "00:00" is 5 chars. We want it to fit comfortably
        # in the width with margin. Empirically, dividing width by ~5.5
        # gives a good character size in points.
        # Also constrain by height so it doesn't overpower a short docker.
        from_width = width / 5.5
        from_height = height / 5.5  # time label gets ~1/5 of vertical space
        
        time_pt = int(min(from_width, from_height))
        time_pt = max(self.TIME_MIN_PT, min(self.TIME_MAX_PT, time_pt))
        
        status_pt = int(time_pt * self.STATUS_RATIO)
        status_pt = max(self.STATUS_MIN_PT, min(self.STATUS_MAX_PT, status_pt))
        
        # Apply time font
        time_font = QFont()
        time_font.setPointSize(time_pt)
        time_font.setWeight(QFont.Light)  # font-weight: 200 equivalent
        self.time_label.setFont(time_font)
        
        # Reserve enough vertical space so layout doesn't clip the label
        fm_time = QFontMetrics(time_font)
        self.time_label.setMinimumHeight(fm_time.height() + 6)
        
        # Apply status font
        status_font = QFont()
        status_font.setPointSize(status_pt)
        self.status_label.setFont(status_font)
        
        fm_status = QFontMetrics(status_font)
        self.status_label.setMinimumHeight(fm_status.height() + 2)
    
    # ── Tick ──
    def _on_tick(self):
        if self.state != self.STATE_RUNNING:
            return
        self.remaining -= 1
        if self.remaining <= 0:
            self._start_break()
        self._refresh_display()
    
    # ── Display ──
    def _refresh_display(self):
        m, s = divmod(max(0, self.remaining), 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")
        
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
    
    # ── Buttons ──
    def _on_pause_clicked(self):
        if self.state == self.STATE_RUNNING:
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.state = self.STATE_RUNNING
        self._refresh_display()
    
    def _on_reset_clicked(self):
        if self.overlay is not None:
            self.overlay.close()
            self.overlay = None
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self._refresh_display()
    
    def _on_config_clicked(self):
        dialog = ConfigDialog(self.config, parent=self.widget())
        if dialog.exec_():
            dialog.apply_to_config()
            if self.state == self.STATE_RUNNING:
                if self.remaining > self.config.work_seconds:
                    self.remaining = self.config.work_seconds
            else:
                self.remaining = self.config.work_seconds
            self._refresh_display()
    
    # ── Break flow ──
    def _start_break(self):
        self.state = self.STATE_BREAK
        self.remaining = 0
        self._refresh_display()
        
        self.overlay = CalmBreakOverlay(
            break_seconds=self.config.break_seconds
        )
        self.overlay.breakFinished.connect(self._end_break)
        self.overlay.show()
    
    def _end_break(self):
        self.overlay = None
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self._refresh_display()
    
    def canvasChanged(self, canvas):
        pass
