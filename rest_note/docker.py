import os

from .compat import (
    Qt,
    QSize,
    QTimer,
    QWidget,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QDockWidget,
    QFont,
    QFontMetrics,
    QIcon,
)

_ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")

from .config_manager import ConfigManager
from .config_dialog import ConfigDialog
from .overlay import CalmBreakOverlay
from .micro_toast import MicroBreakToast
from .idle_detector import IdleDetector

from krita import DockWidgetFactoryBase


class RestNoteDockerWidget(QDockWidget):
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_BREAK = "break"
    STATE_MICRO_BREAK = "micro_break"
    STATE_IDLE = "idle"

    # Font scaling
    TIME_MIN_PT = 14
    TIME_MAX_PT = 96
    STATUS_MIN_PT = 8
    STATUS_MAX_PT = 24
    SUB_MIN_PT = 8
    SUB_MAX_PT = 18
    STATUS_RATIO = 0.28
    SUB_RATIO = 0.22

    # Button scaling
    BTN_MIN_PX = 16
    BTN_MAX_PX = 64
    BTN_RATIO = 0.5

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rest Note")

        self.config = ConfigManager()
        self.state = self.STATE_RUNNING

        # Big break countdown (seconds)
        self.remaining = self.config.work_seconds
        # Micro break countdown (seconds until next eye break)
        self.micro_remaining = self.config.micro_interval_seconds

        self.overlay = None  # CalmBreakOverlay instance
        self.micro_toast = None  # MicroBreakToast instance
        self.idle_detector = None

        self._apply_idle_config()

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
        self.status_label.setStyleSheet("color: #b8b8b8; letter-spacing: 2px;")
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

        self._icon_pause = QIcon(os.path.join(_ICONS_DIR, "pause.png"))
        self._icon_resume = QIcon(os.path.join(_ICONS_DIR, "play.png"))
        self._icon_refresh = QIcon(os.path.join(_ICONS_DIR, "refresh.png"))
        self._icon_setting = QIcon(os.path.join(_ICONS_DIR, "setting.png"))

        _btn_style = "background-color: rgb(70, 70, 70);"

        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(self._icon_pause)
        self.pause_btn.setStyleSheet(_btn_style)
        self.pause_btn.setToolTip("Pause / Resume")
        self.pause_btn.clicked.connect(self._on_pause_clicked)

        self.reset_btn = QPushButton()
        self.reset_btn.setIcon(self._icon_refresh)
        self.reset_btn.setStyleSheet(_btn_style)
        self.reset_btn.setToolTip("Reset")
        self.reset_btn.clicked.connect(self._on_reset_clicked)

        self.config_btn = QPushButton()
        self.config_btn.setIcon(self._icon_setting)
        self.config_btn.setStyleSheet(_btn_style)
        self.config_btn.setToolTip("Config…")
        self.config_btn.clicked.connect(self._on_config_clicked)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.pause_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.config_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

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

        btn_px = int(time_pt * self.BTN_RATIO)
        btn_px = max(self.BTN_MIN_PX, min(self.BTN_MAX_PX, btn_px))
        btn_sz = QSize(btn_px, btn_px)
        for btn in (self.pause_btn, self.reset_btn, self.config_btn):
            btn.setFixedSize(btn_sz)
            btn.setIconSize(btn_sz)

    # ── Tick: heart of the integration ──
    def _on_tick(self):
        # 1. Idle detection
        self._check_idle_transition()

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

    # ── Idle handling ──
    def _apply_idle_config(self):
        """Create or destroy IdleDetector to match the current config."""
        if self.config.idle_enabled:
            if self.idle_detector is None:
                self.idle_detector = IdleDetector()
        else:
            if self.idle_detector is not None:
                self.idle_detector.destroy()
                self.idle_detector = None
            if self.state == self.STATE_IDLE:
                self.state = self.STATE_RUNNING

    def _check_idle_transition(self):
        """Auto-transition between RUNNING and IDLE based on user input."""
        if self.idle_detector is None:
            return

        idle_sec = self.idle_detector.idle_seconds()
        threshold = self.config.idle_threshold_seconds

        if self.state == self.STATE_RUNNING:
            if idle_sec >= threshold:
                self.state = self.STATE_IDLE

        elif self.state == self.STATE_IDLE:
            if idle_sec < threshold:
                self.state = self.STATE_RUNNING

        # PAUSED, BREAK, MICRO_BREAK: idle detection is intentionally
        # skipped to avoid interfering with explicit user/system states.

    def _current_screen(self):
        """Resolve the screen the Krita main window is currently on."""
        win = self.window()
        if win is not None:
            handle = win.windowHandle()
            if handle is not None and handle.screen() is not None:
                return handle.screen()
            screen = win.screen()
            if screen is not None:
                return screen
        return QApplication.primaryScreen()

    # ── Micro break logic ──
    def _maybe_trigger_micro_break(self):
        """20分タイマーが0になった時に呼ばれる。大休憩が近ければスキップ。"""
        # 大休憩との近接スキップ
        if self.remaining <= self.config.micro_skip_threshold:
            self.micro_remaining = self.config.micro_interval_seconds
            return

        self.state = self.STATE_MICRO_BREAK
        self.micro_toast = MicroBreakToast(
            duration_seconds=self.config.micro_duration_seconds,
            margin=self.config.micro_toast_margin,
            width=self.config.micro_toast_width,
            height=self.config.micro_toast_height,
            title_font_size=self.config.micro_toast_title_font_size,
            message_font_size=self.config.micro_toast_message_font_size,
            screen=self._current_screen(),
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
            break_seconds=self.config.break_seconds,
            title_font_size=self.config.overlay_title_font_size,
            message_font_size=self.config.overlay_message_font_size,
            skip_font_size=self.config.overlay_skip_font_size,
            screen=self._current_screen(),
        )
        self.overlay.breakFinished.connect(self._end_big_break)
        self.overlay.show()

    def _end_big_break(self):
        self.overlay = None
        self.state = self.STATE_RUNNING
        self.remaining = self.config.work_seconds
        self.micro_remaining = self.config.micro_interval_seconds
        if self.idle_detector is not None:
            self.idle_detector.reset()
        self._refresh_display()

    # ── Display ──
    def _refresh_display(self):
        m, s = divmod(max(0, self.remaining), 60)
        self.time_label.setText(f"{m:02d}:{s:02d}")

        # Status
        if self.state == self.STATE_RUNNING:
            self.status_label.setText("WORKING")
            self.pause_btn.setIcon(self._icon_pause)
            self.pause_btn.setEnabled(True)
        elif self.state == self.STATE_PAUSED:
            self.status_label.setText("PAUSED")
            self.pause_btn.setIcon(self._icon_resume)
            self.pause_btn.setEnabled(True)
        elif self.state == self.STATE_BREAK:
            self.status_label.setText("ON BREAK")
            self.pause_btn.setEnabled(False)
        elif self.state == self.STATE_MICRO_BREAK:
            self.status_label.setText("EYE BREAK")
            self.pause_btn.setEnabled(True)
        elif self.state == self.STATE_IDLE:
            self.status_label.setText("IDLE")
            self.pause_btn.setIcon(self._icon_pause)
            self.pause_btn.setEnabled(True)

        # Sub-label: next eye break info
        if self.state == self.STATE_IDLE:
            self.sub_label.setText("Away — timer paused")
        elif not self.config.micro_enabled:
            self.sub_label.setText("Eye breaks: disabled")
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
            if self.idle_detector is not None:
                self.idle_detector.reset()
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
        if self.idle_detector is not None:
            self.idle_detector.reset()
        self._refresh_display()

    def _on_config_clicked(self):
        dialog = ConfigDialog(self.config, parent=self.widget())
        if dialog.exec():
            dialog.apply_to_config()
            self._apply_idle_config()
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

    def closeEvent(self, event):
        if self.tick_timer is not None:
            self.tick_timer.stop()
        if self.idle_detector is not None:
            self.idle_detector.destroy()
            self.idle_detector = None
        if self.overlay is not None:
            self.overlay.close()
            self.overlay = None
        if self.micro_toast is not None:
            self.micro_toast.cancel()
            self.micro_toast = None
        super().closeEvent(event)


class RestNoteDockerFactory(DockWidgetFactoryBase):

    def __init__(self):

        try:
            _dock_pos = DockWidgetFactoryBase.DockRight
        except AttributeError:
            _dock_pos = DockWidgetFactoryBase.DockPosition.DockRight  # Krita 6

        super().__init__("RestNoteDocker", _dock_pos)

    def createDockWidget(self):
        return RestNoteDockerWidget()
