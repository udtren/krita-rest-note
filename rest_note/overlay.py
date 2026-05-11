from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, pyqtProperty, QEasingCurve
)
from PyQt5.QtGui import QPainter, QColor

from .progress_button import CalmProgressButton


class CalmBreakOverlay(QWidget):
    breakFinished = pyqtSignal()
    
    def __init__(self, break_seconds=600):
        super().__init__()
        self.break_seconds = break_seconds
        
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        self._bg_alpha = 0
        self.target_alpha = 235
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(36)
        
        title = QLabel("Time for a break")
        title.setStyleSheet("""
            color: rgba(230, 220, 205, 200);
            font-size: 40px;
            font-weight: 200;
            letter-spacing: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        minutes = max(1, break_seconds // 60)
        self.message = QLabel(
            f"{minutes}-minute break.\n"
            f"Look into the distance and let your eyes relax."
        )
        self.message.setStyleSheet("""
            color: rgba(210, 200, 185, 160);
            font-size: 18px;
        """)
        self.message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message)
        
        self.button = CalmProgressButton(break_seconds, "Resume work")
        self.button.clicked.connect(self._on_resume)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        
        self.fade_anim = QPropertyAnimation(self, b"bgAlpha")
        self.fade_anim.setDuration(30_000)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(self.target_alpha)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutSine)
        QTimer.singleShot(0, self.fade_anim.start)
    
    def get_bg_alpha(self):
        return self._bg_alpha
    
    def set_bg_alpha(self, value):
        self._bg_alpha = value
        self.update()
    
    bgAlpha = pyqtProperty(int, fget=get_bg_alpha, fset=set_bg_alpha)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(15, 17, 22, self._bg_alpha))
    
    def _on_resume(self):
        self.breakFinished.emit()
        self.close()
