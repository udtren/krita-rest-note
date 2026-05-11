from .compat import (
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox,
    QVBoxLayout, QCheckBox, QGroupBox,
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
        big_form = QFormLayout(big_group)

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
            "Skip eye break if the next big break is closer than this."
        )
        micro_form.addRow("Skip if big break within:", self.micro_skip_spin)

        micro_layout.addLayout(micro_form)
        outer.addWidget(micro_group)

        self._update_micro_enabled(self.micro_enable.isChecked())

        # ── Idle detection group ──
        idle_group = QGroupBox("Idle detection")
        idle_layout = QVBoxLayout(idle_group)

        self.idle_enable = QCheckBox("Enable idle detection")
        self.idle_enable.setChecked(self.config.idle_enabled)
        self.idle_enable.setToolTip(
            "Pause the work timer automatically when no input is detected."
        )
        self.idle_enable.toggled.connect(self._update_idle_enabled)
        idle_layout.addWidget(self.idle_enable)

        idle_form = QFormLayout()
        self.idle_threshold_spin = QSpinBox()
        self.idle_threshold_spin.setRange(5, 3600)
        self.idle_threshold_spin.setSuffix(" sec")
        self.idle_threshold_spin.setValue(self.config.idle_threshold_seconds)
        idle_form.addRow("Idle threshold:", self.idle_threshold_spin)
        idle_layout.addLayout(idle_form)

        outer.addWidget(idle_group)

        self._update_idle_enabled(self.idle_enable.isChecked())

        # ── Overlay appearance group ──
        overlay_group = QGroupBox("Overlay appearance")
        overlay_form = QFormLayout(overlay_group)

        self.overlay_title_font_spin = QSpinBox()
        self.overlay_title_font_spin.setRange(6, 200)
        self.overlay_title_font_spin.setSuffix(" px")
        self.overlay_title_font_spin.setValue(self.config.overlay_title_font_size)
        overlay_form.addRow("Title font size:", self.overlay_title_font_spin)

        self.overlay_msg_font_spin = QSpinBox()
        self.overlay_msg_font_spin.setRange(6, 200)
        self.overlay_msg_font_spin.setSuffix(" px")
        self.overlay_msg_font_spin.setValue(self.config.overlay_message_font_size)
        overlay_form.addRow("Message font size:", self.overlay_msg_font_spin)

        self.overlay_skip_font_spin = QSpinBox()
        self.overlay_skip_font_spin.setRange(6, 200)
        self.overlay_skip_font_spin.setSuffix(" px")
        self.overlay_skip_font_spin.setValue(self.config.overlay_skip_font_size)
        overlay_form.addRow("Skip font size:", self.overlay_skip_font_spin)

        outer.addWidget(overlay_group)

        # ── Toast appearance group ──
        toast_group = QGroupBox("Toast appearance")
        toast_form = QFormLayout(toast_group)

        self.toast_margin_spin = QSpinBox()
        self.toast_margin_spin.setRange(0, 200)
        self.toast_margin_spin.setSuffix(" px")
        self.toast_margin_spin.setValue(self.config.micro_toast_margin)
        toast_form.addRow("Margin:", self.toast_margin_spin)

        self.toast_width_spin = QSpinBox()
        self.toast_width_spin.setRange(100, 800)
        self.toast_width_spin.setSuffix(" px")
        self.toast_width_spin.setValue(self.config.micro_toast_width)
        toast_form.addRow("Width:", self.toast_width_spin)

        self.toast_height_spin = QSpinBox()
        self.toast_height_spin.setRange(50, 400)
        self.toast_height_spin.setSuffix(" px")
        self.toast_height_spin.setValue(self.config.micro_toast_height)
        toast_form.addRow("Height:", self.toast_height_spin)

        self.toast_title_font_spin = QSpinBox()
        self.toast_title_font_spin.setRange(6, 48)
        self.toast_title_font_spin.setSuffix(" px")
        self.toast_title_font_spin.setValue(self.config.micro_toast_title_font_size)
        toast_form.addRow("Title font size:", self.toast_title_font_spin)

        self.toast_msg_font_spin = QSpinBox()
        self.toast_msg_font_spin.setRange(6, 48)
        self.toast_msg_font_spin.setSuffix(" px")
        self.toast_msg_font_spin.setValue(self.config.micro_toast_message_font_size)
        toast_form.addRow("Message font size:", self.toast_msg_font_spin)

        outer.addWidget(toast_group)

        # ── OK / Cancel ──
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def _update_micro_enabled(self, enabled):
        self.micro_interval_spin.setEnabled(enabled)
        self.micro_duration_spin.setEnabled(enabled)
        self.micro_skip_spin.setEnabled(enabled)

    def _update_idle_enabled(self, enabled):
        self.idle_threshold_spin.setEnabled(enabled)

    def apply_to_config(self):
        self.config.work_minutes = self.work_spin.value()
        self.config.break_minutes = self.break_spin.value()
        self.config.micro_enabled = self.micro_enable.isChecked()
        self.config.micro_interval_minutes = self.micro_interval_spin.value()
        self.config.micro_duration_seconds = self.micro_duration_spin.value()
        self.config.micro_skip_threshold = self.micro_skip_spin.value()
        self.config.idle_enabled = self.idle_enable.isChecked()
        self.config.idle_threshold_seconds = self.idle_threshold_spin.value()
        self.config.micro_toast_margin = self.toast_margin_spin.value()
        self.config.micro_toast_width = self.toast_width_spin.value()
        self.config.micro_toast_height = self.toast_height_spin.value()
        self.config.micro_toast_title_font_size = self.toast_title_font_spin.value()
        self.config.micro_toast_message_font_size = self.toast_msg_font_spin.value()
        self.config.overlay_title_font_size = self.overlay_title_font_spin.value()
        self.config.overlay_message_font_size = self.overlay_msg_font_spin.value()
        self.config.overlay_skip_font_size = self.overlay_skip_font_spin.value()
        self.config.save()
