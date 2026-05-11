"""PyQt5 / PyQt6 compatibility shim.

Import all Qt symbols from this module instead of directly from PyQt5 or PyQt6.
"""

try:
    from PyQt5.QtCore import (  # noqa: F401
        Qt, QObject, QEvent, QTimer, QSize, QPoint, QRectF, QTime,
        pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve,
    )
    from PyQt5.QtWidgets import (  # noqa: F401
        QWidget, QApplication, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QDockWidget,
        QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
        QCheckBox, QGroupBox,
    )
    from PyQt5.QtGui import (  # noqa: F401
        QFont, QFontMetrics, QIcon, QPainter, QColor, QPen, QPainterPath,
    )
    PYQT6 = False

except ImportError:
    from PyQt6.QtCore import (  # noqa: F401
        Qt, QObject, QEvent, QTimer, QSize, QPoint, QRectF, QTime,
        pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve,
    )
    from PyQt6.QtWidgets import (  # noqa: F401
        QWidget, QApplication, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QDockWidget,
        QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
        QCheckBox, QGroupBox,
    )
    from PyQt6.QtGui import (  # noqa: F401
        QFont, QFontMetrics, QIcon, QPainter, QColor, QPen, QPainterPath,
    )
    PYQT6 = True

    # Alignment
    Qt.AlignLeft    = Qt.AlignmentFlag.AlignLeft
    Qt.AlignRight   = Qt.AlignmentFlag.AlignRight
    Qt.AlignCenter  = Qt.AlignmentFlag.AlignCenter
    Qt.AlignHCenter = Qt.AlignmentFlag.AlignHCenter
    Qt.AlignVCenter = Qt.AlignmentFlag.AlignVCenter

    # Window flags
    Qt.FramelessWindowHint       = Qt.WindowType.FramelessWindowHint
    Qt.WindowStaysOnTopHint      = Qt.WindowType.WindowStaysOnTopHint
    Qt.Tool                      = Qt.WindowType.Tool
    Qt.WindowTransparentForInput = Qt.WindowType.WindowTransparentForInput

    # Widget attributes
    Qt.WA_TranslucentBackground = Qt.WidgetAttribute.WA_TranslucentBackground
    Qt.WA_ShowWithoutActivating = Qt.WidgetAttribute.WA_ShowWithoutActivating

    # Cursor shapes
    Qt.ArrowCursor        = Qt.CursorShape.ArrowCursor
    Qt.PointingHandCursor = Qt.CursorShape.PointingHandCursor

    # Brush style
    Qt.NoBrush = Qt.BrushStyle.NoBrush

    # QEvent types
    QEvent.KeyPress           = QEvent.Type.KeyPress
    QEvent.KeyRelease         = QEvent.Type.KeyRelease
    QEvent.MouseMove          = QEvent.Type.MouseMove
    QEvent.MouseButtonPress   = QEvent.Type.MouseButtonPress
    QEvent.MouseButtonRelease = QEvent.Type.MouseButtonRelease
    QEvent.Wheel              = QEvent.Type.Wheel
    QEvent.TabletMove         = QEvent.Type.TabletMove
    QEvent.TabletPress        = QEvent.Type.TabletPress

    # QFrame
    QFrame.HLine = QFrame.Shape.HLine

    # QDialogButtonBox
    QDialogButtonBox.Ok     = QDialogButtonBox.StandardButton.Ok
    QDialogButtonBox.Cancel = QDialogButtonBox.StandardButton.Cancel

    # QFont
    QFont.Light = QFont.Weight.Light

    # QEasingCurve
    QEasingCurve.OutCubic  = QEasingCurve.Type.OutCubic
    QEasingCurve.InCubic   = QEasingCurve.Type.InCubic
    QEasingCurve.InOutSine = QEasingCurve.Type.InOutSine

    # QPainter
    QPainter.Antialiasing = QPainter.RenderHint.Antialiasing
