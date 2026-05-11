from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QLabel, QVBoxLayout
)


class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Rest Note — Configuration")
        self.setMinimumWidth(320)
        
        outer = QVBoxLayout(self)
        
        info = QLabel("Set work and break durations (in minutes).")
        info.setWordWrap(True)
        outer.addWidget(info)
        
        form = QFormLayout()
        
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setSuffix(" min")
        self.work_spin.setValue(self.config.work_minutes)
        form.addRow("Work duration:", self.work_spin)
        
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setValue(self.config.break_minutes)
        form.addRow("Break duration:", self.break_spin)
        
        outer.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
    
    def apply_to_config(self):
        self.config.work_minutes = self.work_spin.value()
        self.config.break_minutes = self.break_spin.value()
        self.config.save()
