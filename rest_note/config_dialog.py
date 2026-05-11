from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QLabel, QVBoxLayout,
    QCheckBox, QGroupBox
)


class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Rest Note — Configuration")
        self.setMinimumWidth(360)
        
        outer = QVBoxLayout(self)
        
        # ── Big break group ──
        big_group = QGroupBox("Work / Break cycle")
        big_layout = QVBoxLayout(big_group)
        
        self.work_enable = QCheckBox("Enable scheduled work breaks")
        self.work_enable.setChecked(self.config.work_break_enabled)
        self.work_enable.toggled.connect(self._update_work_enabled)
        big_layout.addWidget(self.work_enable)
        
        big_form = QFormLayout()
        
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setSuffix(" min")
        self.work_spin.setValue(self.config.work_minutes)
        big_form.addRow("Work duration:", self.work_spin)
        
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setValue(self.config.break_minutes)
        big_form.addRow("Break duration:", self.break_spin)
        
        big_layout.addLayout(big_form)
        outer.addWidget(big_group)
        
        # ── Micro break group (20-20-20) ──
        micro_group = QGroupBox("Eye break reminder (20-20-20)")
        micro_layout = QVBoxLayout(micro_group)
        
        self.micro_enable = QCheckBox("Enable eye break reminders")
        self.micro_enable.setChecked(self.config.micro_enabled)
        self.micro_enable.toggled.connect(self._update_micro_enabled)
        micro_layout.addWidget(self.micro_enable)
        
        micro_form = QFormLayout()
        
        self.micro_interval_spin = QSpinBox()
        self.micro_interval_spin.setRange(1, 60)
        self.micro_interval_spin.setSuffix(" min")
        self.micro_interval_spin.setValue(self.config.micro_interval_minutes)
        micro_form.addRow("Interval:", self.micro_interval_spin)
        
        self.micro_duration_spin = QSpinBox()
        self.micro_duration_spin.setRange(5, 120)
        self.micro_duration_spin.setSuffix(" sec")
        self.micro_duration_spin.setValue(self.config.micro_duration_seconds)
        micro_form.addRow("Duration:", self.micro_duration_spin)
        
        self.micro_skip_spin = QSpinBox()
        self.micro_skip_spin.setRange(0, 600)
        self.micro_skip_spin.setSuffix(" sec")
        self.micro_skip_spin.setValue(self.config.micro_skip_threshold)
        self.micro_skip_spin.setToolTip(
            "Skip eye break if the next work break is closer than this. "
            "Has no effect when work breaks are disabled."
        )
        micro_form.addRow("Skip if work break within:", self.micro_skip_spin)
        
        micro_layout.addLayout(micro_form)
        outer.addWidget(micro_group)
        
        # ── Warning label (both disabled) ──
        self.warning_label = QLabel(
            "⚠ No breaks are scheduled. The plugin will stay idle."
        )
        self.warning_label.setStyleSheet(
            "color: #c8a060; font-size: 11px; padding: 4px;"
        )
        self.warning_label.setWordWrap(True)
        outer.addWidget(self.warning_label)
        
        # ── Initial enabled states ──
        self._update_work_enabled(self.work_enable.isChecked())
        self._update_micro_enabled(self.micro_enable.isChecked())
        
        # ── OK / Cancel ──
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
    
    def _update_work_enabled(self, enabled):
        self.work_spin.setEnabled(enabled)
        self.break_spin.setEnabled(enabled)
        self._update_warning()
    
    def _update_micro_enabled(self, enabled):
        self.micro_interval_spin.setEnabled(enabled)
        self.micro_duration_spin.setEnabled(enabled)
        self.micro_skip_spin.setEnabled(enabled)
        self._update_warning()
    
    def _update_warning(self):
        both_off = (
            not self.work_enable.isChecked() 
            and not self.micro_enable.isChecked()
        )
        self.warning_label.setVisible(both_off)
    
    def apply_to_config(self):
        self.config.work_break_enabled = self.work_enable.isChecked()
        self.config.work_minutes = self.work_spin.value()
        self.config.break_minutes = self.break_spin.value()
        self.config.micro_enabled = self.micro_enable.isChecked()
        self.config.micro_interval_minutes = self.micro_interval_spin.value()
        self.config.micro_duration_seconds = self.micro_duration_spin.value()
        self.config.micro_skip_threshold = self.micro_skip_spin.value()
        self.config.save()
