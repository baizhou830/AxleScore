from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QSpinBox,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import data_manager as dm

COMBO_STYLE = """
    QComboBox {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QComboBox::drop-down { border: none; }
"""

SMALL_COMBO_STYLE = """
    QComboBox {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 3px 6px;
        background: white; color: #1e2026; font-size: 11px;
    }
    QComboBox::drop-down { border: none; }
"""

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QLineEdit:focus { border-color: #5078f0; }
"""

SPIN_STYLE = """
    QSpinBox {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
        min-width: 60px;
    }
"""

ACCENT_BTN_STYLE = """
    QPushButton {
        background: #5078f0; color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #6090E8; }
"""

DANGER_BTN_STYLE = """
    QPushButton {
        background: #E55;
        color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #D44; }
"""

TEXT_BTN_STYLE = """
    QPushButton {
        background: transparent; color: #787d88;
        border: none; font-size: 11px;
    }
    QPushButton:hover { color: #5078f0; }
"""

GROUP_STYLE = """
    QGroupBox {
        border: 1px solid #ebedf1;
        border-radius: 8px; margin-top: 8px;
        padding: 12px 8px 8px 8px;
        font-size: 12px; color: #787d88;
    }
    QGroupBox::title {
        subcontrol-origin: margin; left: 12px; padding: 0 4px;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        border: 1px solid #ebedf1;
        border-radius: 8px; background: white;
        gridline-color: #ebedf1;
        font-size: 12px; color: #1e2026;
    }
    QTableWidget::item { padding: 6px; }
    QHeaderView::section {
        background: #f6f7f9; border: none;
        border-bottom: 1px solid #ebedf1;
        padding: 8px; font-weight: bold; color: #787d88;
    }
"""

LOG_STYLE = """
    QTextEdit {
        border: 1px solid #ebedf1;
        border-radius: 8px; background: #f6f7f9;
        font-size: 11px; color: #787d88; padding: 8px;
    }
"""

LABEL_STYLE = "color: #787d88; font-size: 12px;"


class ScorePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #fbfbfd;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)

        #顶部：周次选择,新建周次
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        top_row.addWidget(self._label("当前周次:"))
        self.week_combo = QComboBox()
        self.week_combo.setMinimumWidth(100)
        self.week_combo.setStyleSheet(COMBO_STYLE)
        self.week_combo.currentTextChanged.connect(self._on_week_changed)
        top_row.addWidget(self.week_combo)

        self.add_week_btn = QPushButton("+ 新建周次")
        self.add_week_btn.setStyleSheet(ACCENT_BTN_STYLE)
        self.add_week_btn.clicked.connect(self._add_week)
        top_row.addWidget(self.add_week_btn)
        top_row.addStretch()

        layout.addLayout(top_row)

        #分数操作
        op_group = QGroupBox("分数操作")
        op_group.setStyleSheet(GROUP_STYLE)
        op_layout = QHBoxLayout(op_group)
        op_layout.setSpacing(8)

        op_layout.addWidget(self._label("小组:"))
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(80)
        self.group_combo.setStyleSheet(COMBO_STYLE)
        op_layout.addWidget(self.group_combo)

        op_layout.addWidget(self._label("分值:"))
        self.score_spin = QSpinBox()
        self.score_spin.setRange(-999, 999)
        self.score_spin.setValue(1)
        self.score_spin.setStyleSheet(SPIN_STYLE)
        op_layout.addWidget(self.score_spin)

        op_layout.addWidget(self._label("原因:"))
        self.reason_input = QComboBox()
        self.reason_input.setEditable(True)
        self.reason_input.addItems(["回答问题", "课堂表现", "作业完成", "背课文", "违纪", "额外加分", "其他"])
        self.reason_input.setPlaceholderText("可选")
        self.reason_input.setMaximumWidth(120)
        self.reason_input.setStyleSheet(SMALL_COMBO_STYLE)
        op_layout.addWidget(self.reason_input)

        self.add_btn = QPushButton("+ 加分")
        self.add_btn.setStyleSheet(ACCENT_BTN_STYLE)
        self.add_btn.clicked.connect(lambda: self._modify_score(True))
        op_layout.addWidget(self.add_btn)

        self.sub_btn = QPushButton("- 减分")
        self.sub_btn.setStyleSheet(DANGER_BTN_STYLE)
        self.sub_btn.clicked.connect(lambda: self._modify_score(False))
        op_layout.addWidget(self.sub_btn)

        layout.addWidget(op_group)

        #分数表
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, stretch=1)

        #操作日志
        log_row = QHBoxLayout()
        log_row.addWidget(self._label("操作日志"))
        log_row.addStretch()
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.setStyleSheet(TEXT_BTN_STYLE)
        clear_log_btn.clicked.connect(self._clear_logs)
        log_row.addWidget(clear_log_btn)
        layout.addLayout(log_row)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(100)
        self.log_view.setStyleSheet(LOG_STYLE)
        layout.addWidget(self.log_view)

    #操作

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        #周次下拉
        self.week_combo.blockSignals(True)
        self.week_combo.clear()
        weeks = dm.get_weeks()
        self.week_combo.addItems(weeks)
        if weeks:
            self.week_combo.setCurrentIndex(len(weeks) - 1)
        self.week_combo.blockSignals(False)

        #小组下拉
        self.group_combo.clear()
        self.group_combo.addItems(dm.get_groups())

        self._refresh_table()
        self._refresh_logs()

    def _on_week_changed(self):
        self._refresh_table()

    def _refresh_table(self):
        week = self.week_combo.currentText()
        if not week:
            self.table.setRowCount(0)
            return

        scores = dm.get_scores()
        week_data = scores.get(week, {})
        groups = dm.get_groups()

        self.table.setRowCount(len(groups))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["小组", "本周分数", "累计总分", "排名"])

        #计算排名
        totals = [(g, dm.get_group_total(g)) for g in groups]
        totals.sort(key=lambda x: -x[1])
        rank_map = {g: i + 1 for i, (g, _) in enumerate(totals)}

        for row, g in enumerate(groups):
            self.table.setItem(row, 0, QTableWidgetItem(g))
            score = week_data.get(g, 0)
            self.table.setItem(row, 1, QTableWidgetItem(str(score)))
            total = dm.get_group_total(g)
            self.table.setItem(row, 2, QTableWidgetItem(str(total)))
            self.table.setItem(row, 3, QTableWidgetItem(f"#{rank_map.get(g, '-')}"))

            #分数着色
            if score > 0:
                self.table.item(row, 1).setForeground(QColor(80, 120, 240))
            elif score < 0:
                self.table.item(row, 1).setForeground(QColor(220, 60, 60))

    def _refresh_logs(self):
        logs = dm.get_logs()
        lines = []
        for log in reversed(logs[-50:]):
            lines.append(f"[{log['time']}] {log['action']}: {log['detail']}")
        self.log_view.setPlainText("\n".join(lines))
        # 滚动到顶部
        cursor = self.log_view.textCursor()
        cursor.movePosition(cursor.Start)
        self.log_view.setTextCursor(cursor)

    def _add_week(self):
        ok, msg = dm.add_week()
        if ok:
            self.refresh()
        else:
            QMessageBox.warning(self, "提示", msg)

    def _modify_score(self, is_add):
        group = self.group_combo.currentText()
        week = self.week_combo.currentText()
        value = self.score_spin.value()
        reason = self.reason_input.currentText().strip()

        if not group or not week:
            QMessageBox.warning(self, "提示", "请选择小组和周次")
            return

        if not is_add:
            value = -value

        ok, msg = dm.add_score(group, week, value, reason)
        if ok:
            self.reason_input.clear()
            self._refresh_table()
            self._refresh_logs()
        else:
            QMessageBox.warning(self, "提示", msg)

    def _clear_logs(self):
        dm.clear_logs()
        self._refresh_logs()

    #样式辅助

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_STYLE)
        return lbl
