from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, pyqtProperty, QEasingCurve,
    QPoint, QRectF
)
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath


class MicroBreakToast(QWidget):
    """
    Small unobtrusive toast in screen corner for 20-20-20 reminders.
    - Stays on top but doesn't block input
    - Fades in, holds, fades out
    - Shows simple text + thin progress bar that drains
    """
    finished = pyqtSignal()
    
    MARGIN = 24   # margin from screen edge
    WIDTH = 320
    HEIGHT = 110
    
    def __init__(self, duration_seconds=20):
        super().__init__()
        self.duration = duration_seconds
        self.elapsed = 0.0
        
        # Non-blocking, always-on-top, frameless
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput  # クリックを下に通す
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # フォーカスを奪わない
        self.resize(self.WIDTH, self.HEIGHT)
        
        # Position: bottom-right of primary screen
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.WIDTH - self.MARGIN
        y = screen.bottom() - self.HEIGHT - self.MARGIN
        self.move(QPoint(x, y))
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)
        
        self.title_label = QLabel("Eye break")
        self.title_label.setStyleSheet(
            "color: rgba(230,220,205,220); font-size: 13px; letter-spacing: 3px;"
        )
        layout.addWidget(self.title_label)
        
        self.message_label = QLabel("Look ~6m away for 20 seconds.")
        self.message_label.setStyleSheet(
            "color: rgba(245,235,220,200); font-size: 15px;"
        )
        layout.addWidget(self.message_label)
        
        layout.addStretch(1)
        
        # Opacity animation for fade-in / fade-out
        self._opacity = 0.0
        self.setWindowOpacity(0.0)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(1200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self._on_fade_out_done)
        
        # Tick timer for progress bar
        self.tick_interval_ms = 100
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
    
    def show(self):
        super().show()
        self.fade_in.start()
        self.timer.start(self.tick_interval_ms)
    
    def _tick(self):
        self.elapsed += self.tick_interval_ms / 1000.0
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.timer.stop()
            self.fade_out.start()
        self.update()
    
    def _on_fade_out_done(self):
        self.finished.emit()
        self.close()
    
    def cancel(self):
        """外部から強制終了するときに呼ぶ"""
        self.timer.stop()
        if self.fade_in.state() == QPropertyAnimation.Running:
            self.fade_in.stop()
        if self.fade_out.state() != QPropertyAnimation.Running:
            self.fade_out.start()
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 10
        
        # Background: dark calm tone
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path)
        p.fillRect(rect, QColor(28, 30, 36, 235))
        
        # Subtle border
        p.setClipping(False)
        from PyQt5.QtGui import QPen
        p.setPen(QPen(QColor(170, 145, 110, 80), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(rect, radius, radius)
        
        # Thin progress bar at bottom (drains left to right)
        progress = min(1.0, self.elapsed / self.duration)
        bar_height = 3
        bar_y = rect.bottom() - bar_height - 2
        bar_total_w = rect.width() - 4
        bar_x = rect.left() + 2
        # Background of bar
        p.fillRect(QRectF(bar_x, bar_y, bar_total_w, bar_height),
                   QColor(255, 255, 255, 20))
        # Remaining time fills from left, drains as time passes
        remaining_w = bar_total_w * (1.0 - progress)
        p.fillRect(QRectF(bar_x, bar_y, remaining_w, bar_height),
                   QColor(170, 145, 110, 200))
