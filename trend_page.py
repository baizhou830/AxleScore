from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import data_manager as dm

COMBO_STYLE = """
    QComboBox {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QComboBox::drop-down { border: none; }
"""

ACCENT_BTN_STYLE = """
    QPushButton {
        background: #5078f0; color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #6090E8; }
"""

LABEL_STYLE = "color: #787d88; font-size: 12px;"

#中文设置
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class TrendPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #fbfbfd;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)

        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        ctrl_row.addWidget(self._label("查看模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["单周分数", "周对比"])
        self.mode_combo.setStyleSheet(COMBO_STYLE)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        ctrl_row.addWidget(self.mode_combo)

        ctrl_row.addWidget(self._label("周次:"))
        self.week_combo = QComboBox()
        self.week_combo.setMinimumWidth(90)
        self.week_combo.setStyleSheet(COMBO_STYLE)
        self.week_combo.currentTextChanged.connect(self._refresh_chart)
        ctrl_row.addWidget(self.week_combo)

        #对比周次
        self.compare_label = self._label("对比周次:")
        ctrl_row.addWidget(self.compare_label)
        self.compare_combo = QComboBox()
        self.compare_combo.setMinimumWidth(90)
        self.compare_combo.setStyleSheet(COMBO_STYLE)
        self.compare_combo.currentTextChanged.connect(self._refresh_chart)
        ctrl_row.addWidget(self.compare_combo)

        ctrl_row.addStretch()

        refresh_btn = QPushButton("刷新图表")
        refresh_btn.setStyleSheet(ACCENT_BTN_STYLE)
        refresh_btn.clicked.connect(self.soft_refresh)
        ctrl_row.addWidget(refresh_btn)

        layout.addLayout(ctrl_row)

        #图表
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.figure.patch.set_facecolor('#fbfbfd')
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: #fbfbfd; border-radius: 8px;")
        layout.addWidget(self.canvas, stretch=1)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    #作

    def refresh(self):
        weeks = dm.get_weeks()
        self.week_combo.blockSignals(True)
        self.compare_combo.blockSignals(True)
        self.week_combo.clear()
        self.compare_combo.clear()
        self.week_combo.addItems(weeks)
        self.compare_combo.addItems(weeks)
        if len(weeks) >= 2:
            self.week_combo.setCurrentIndex(len(weeks) - 1)
            self.compare_combo.setCurrentIndex(len(weeks) - 2)
        elif weeks:
            self.week_combo.setCurrentIndex(0)
        self.week_combo.blockSignals(False)
        self.compare_combo.blockSignals(False)

        self._on_mode_changed()
        self._refresh_chart()

    def soft_refresh(self):
        weeks = dm.get_weeks()
        cur_week = self.week_combo.currentText()
        cur_compare = self.compare_combo.currentText()

        self.week_combo.blockSignals(True)
        self.compare_combo.blockSignals(True)
        self.week_combo.clear()
        self.compare_combo.clear()
        self.week_combo.addItems(weeks)
        self.compare_combo.addItems(weeks)

        # 尝试恢复之前的选择
        idx = self.week_combo.findText(cur_week)
        self.week_combo.setCurrentIndex(idx if idx >= 0 else max(0, len(weeks) - 1))
        idx2 = self.compare_combo.findText(cur_compare)
        self.compare_combo.setCurrentIndex(idx2 if idx2 >= 0 else max(0, len(weeks) - 2))

        self.week_combo.blockSignals(False)
        self.compare_combo.blockSignals(False)

        self._refresh_chart()

    def _on_mode_changed(self):
        is_compare = self.mode_combo.currentIndex() == 1
        self.compare_label.setVisible(is_compare)
        self.compare_combo.setVisible(is_compare)
        self._refresh_chart()

    def _refresh_chart(self):
        self.ax.clear()
        mode = self.mode_combo.currentIndex()
        week = self.week_combo.currentText()

        if not week:
            self.canvas.draw()
            return

        groups = dm.get_groups()
        scores = dm.get_scores()
        week_data = scores.get(week, {})

        if not groups:
            self.canvas.draw()
            return

        ax = self.ax
        ax.set_facecolor('#FAFBFD')

        if mode == 0:
            #单周柱状图
            values = [week_data.get(g, 0) for g in groups]
            bars = ax.bar(groups, values, color='#B0C4F8', width=0.5, edgecolor='white', linewidth=1)

            #在柱子上方显示数值
            for bar, v in zip(bars, values):
                if v != 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                            str(v), ha='center', va='bottom', fontsize=10,
                            color='#1e2026', fontweight='bold')

            ax.set_title(f'{week} 各组分数', fontsize=14, color='#1e2026', pad=12)
            ax.set_ylabel('分数', fontsize=11, color='#787d88')

        else:
            #周对比
            compare_week = self.compare_combo.currentText()
            if not compare_week:
                self.canvas.draw()
                return

            compare_data = scores.get(compare_week, {})
            x = np.arange(len(groups))
            width = 0.35

            vals1 = [compare_data.get(g, 0) for g in groups]
            vals2 = [week_data.get(g, 0) for g in groups]

            bars1 = ax.bar(x - width / 2, vals1, width, label=compare_week,
                           color='#B0C4F8', edgecolor='white', linewidth=1)
            bars2 = ax.bar(x + width / 2, vals2, width, label=week,
                           color='#5078f0', edgecolor='white', linewidth=1)

            for bar, v in zip(bars1, vals1):
                if v != 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                            str(v), ha='center', va='bottom', fontsize=9,
                            color='#787d88')
            for bar, v in zip(bars2, vals2):
                if v != 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                            str(v), ha='center', va='bottom', fontsize=9,
                            color='#1e2026', fontweight='bold')

            ax.set_xticks(x)
            ax.set_xticklabels(groups)
            ax.set_title(f'{compare_week} vs {week}', fontsize=14,
                         color='#1e2026', pad=12)
            ax.set_ylabel('分数', fontsize=11, color='#787d88')
            ax.legend(fontsize=10, frameon=False)

        ax.tick_params(colors='#787d88', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#ebedf1')
        ax.spines['bottom'].set_color('#ebedf1')
        ax.grid(axis='y', color='#ebedf1', linestyle='--', alpha=0.5)

        self.figure.tight_layout()
        self.canvas.draw()

    #样式

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_STYLE)
        return lbl
