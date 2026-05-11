from .compat import (
    Qt, QTimer, QRectF, pyqtSignal,
    QPushButton,
    QPainter, QColor, QFont, QPen, QPainterPath,
)


class CalmProgressButton(QPushButton):
    readyToClick = pyqtSignal()
    
    def __init__(self, duration_seconds, label="Resume work", parent=None):
        super().__init__(label, parent)
        self.duration = duration_seconds
        self.elapsed = 0.0
        self.label_text = label
        
        self.setEnabled(False)
        self.setMinimumSize(320, 64)
        self.setFont(QFont("", 15))
        self.setCursor(Qt.ArrowCursor)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.tick_interval_ms = 200
        self.timer.start(self.tick_interval_ms)
    
    def _tick(self):
        if self.elapsed >= self.duration:
            return
        self.elapsed += self.tick_interval_ms / 1000.0
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.timer.stop()
            self._on_complete()
        self.update()
    
    def _on_complete(self):
        self.setEnabled(True)
        self.setCursor(Qt.PointingHandCursor)
        self.readyToClick.emit()
    
    def progress(self):
        return min(1.0, self.elapsed / self.duration)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        radius = 8
        
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.setClipPath(path)
        
        t = self.progress()
        is_ready = self.isEnabled()
        
        p.fillRect(rect, QColor(45, 45, 48))
        
        if t > 0:
            fill_width = rect.width() * t
            fill_rect = QRectF(rect.left(), rect.top(), fill_width, rect.height())
            if not is_ready:
                r = int(55 + (75 - 55) * t)
                g = int(55 + (68 - 55) * t)
                b = int(58 + (60 - 58) * t)
                fill_color = QColor(r, g, b)
            else:
                fill_color = QColor(170, 145, 110)
            p.fillRect(fill_rect, fill_color)
        
        p.setClipping(False)
        p.setFont(self.font())
        text_color = QColor(245, 235, 220) if is_ready else QColor(140, 140, 145)
        p.setPen(text_color)
        p.drawText(rect, Qt.AlignCenter, self.label_text)
        
        if is_ready:
            border = QPen(QColor(170, 145, 110, 140), 1.0)
        else:
            border = QPen(QColor(255, 255, 255, 25), 1.0)
        p.setPen(border)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(rect, radius, radius)
