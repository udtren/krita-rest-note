"""
Qt-based idle detector.
Monitors user input events inside the Krita application.

Note: This only detects inactivity inside Krita's windows.
Activity in other applications (browser, etc.) is counted as idle.
"""

from .compat import QObject, QEvent, QTime, QApplication


class IdleDetector(QObject):
    """
    Tracks the time elapsed since the last user input
    inside the Krita application.
    """

    def __init__(self):
        super().__init__()
        self._last_activity = QTime.currentTime()
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (
            QEvent.MouseMove,
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
            QEvent.KeyPress,
            QEvent.KeyRelease,
            QEvent.Wheel,
            QEvent.TabletMove,
            QEvent.TabletPress,
        ):
            self._last_activity = QTime.currentTime()
        return False  # Don't consume the event

    def idle_seconds(self):
        """Seconds since last detected input."""
        return self._last_activity.secsTo(QTime.currentTime())

    def reset(self):
        """Manually mark 'now' as the last activity time."""
        self._last_activity = QTime.currentTime()

    def destroy(self):
        """Remove the event filter and detach from the application."""
        QApplication.instance().removeEventFilter(self)
