from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QListWidget, QListWidgetItem,
                              QMessageBox, QGroupBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import data_manager as dm

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QLineEdit:focus { border-color: #5078f0; }
"""

ACCENT_BTN_STYLE = """
    QPushButton {
        background: #5078f0; color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #6090E8; }
"""

OUTLINE_BTN_STYLE = """
    QPushButton {
        background: transparent; color: #5078f0;
        border: 1px solid #5078f0;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #ebf0ff; }
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

LIST_STYLE = """
    QListWidget {
        border: 1px solid #ebedf1;
        border-radius: 8px; background: white;
        font-size: 12px; color: #1e2026; padding: 4px;
    }
    QListWidget::item {
        padding: 8px 12px; border-bottom: 1px solid #ebedf1;
    }
    QListWidget::item:selected {
        background: #ebf0ff; color: #5078f0;
    }
"""

LABEL_STYLE = "color: #787d88; font-size: 12px;"


class GroupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #fbfbfd;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)

        #添加
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        label = QLabel("新增小组:")
        label.setStyleSheet(LABEL_STYLE)
        add_row.addWidget(label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入小组名称")
        self.name_input.setStyleSheet(INPUT_STYLE)
        add_row.addWidget(self.name_input, stretch=1)

        add_btn = QPushButton("+ 添加")
        add_btn.setStyleSheet(ACCENT_BTN_STYLE)
        add_btn.clicked.connect(self._add_group)
        add_row.addWidget(add_btn)

        layout.addLayout(add_row)

        #列表
        list_group = QGroupBox("小组列表")
        list_group.setStyleSheet(GROUP_STYLE)
        list_layout = QVBoxLayout(list_group)

        self.group_list = QListWidget()
        self.group_list.setStyleSheet(LIST_STYLE)
        list_layout.addWidget(self.group_list)

        # 操作行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        rename_btn = QPushButton("重命名")
        rename_btn.setStyleSheet(OUTLINE_BTN_STYLE)
        rename_btn.clicked.connect(self._rename_group)
        btn_row.addWidget(rename_btn)

        del_btn = QPushButton("删除")
        del_btn.setStyleSheet(DANGER_BTN_STYLE)
        del_btn.clicked.connect(self._remove_group)
        btn_row.addWidget(del_btn)

        btn_row.addStretch()
        list_layout.addLayout(btn_row)

        layout.addWidget(list_group, stretch=1)

        #统计
        stat_group = QGroupBox("统计")
        stat_group.setStyleSheet(GROUP_STYLE)
        stat_layout = QVBoxLayout(stat_group)

        self.stat_label = QLabel("")
        self.stat_label.setWordWrap(True)
        self.stat_label.setStyleSheet("color: #1e2026; font-size: 13px;")
        stat_layout.addWidget(self.stat_label)

        refresh_stat_btn = QPushButton("刷新统计")
        refresh_stat_btn.setStyleSheet(OUTLINE_BTN_STYLE)
        refresh_stat_btn.clicked.connect(self._refresh_stats)
        stat_layout.addWidget(refresh_stat_btn)

        layout.addWidget(stat_group)

    #操作

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        self._refresh_list()
        self._refresh_stats()

    def _refresh_list(self):
        self.group_list.clear()
        groups = dm.get_groups()
        scores = dm.get_scores()
        for g in groups:
            total = dm.get_group_total(g)
            item = QListWidgetItem(f"  {g}    累计: {total} 分")
            item.setData(Qt.UserRole, g)
            self.group_list.addItem(item)

    def _refresh_stats(self):
        groups = dm.get_groups()
        if not groups:
            self.stat_label.setText("暂无小组数据")
            return

        best, best_score = dm.get_highest_score_group()
        totals = [(g, dm.get_group_total(g)) for g in groups]
        totals.sort(key=lambda x: -x[1])

        lines = [f"小组数量: {len(groups)}"]
        if best:
            lines.append(f"最高分小组: {best} ({best_score} 分)")
        lines.append("排行榜:")
        for i, (g, t) in enumerate(totals):
            medal = f"#{i+1}"
            lines.append(f"  {medal}  {g}: {t} 分")

        self.stat_label.setText("\n".join(lines))

    def _add_group(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入小组名称")
            return
        ok, msg = dm.add_group(name)
        if ok:
            self.name_input.clear()
            self.refresh()
        else:
            QMessageBox.warning(self, "提示", msg)

    def _remove_group(self):
        item = self.group_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择一个小组")
            return
        name = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除小组 '{name}' 吗？\n该小组所有分数数据将一并删除。",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = dm.remove_group(name)
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "提示", msg)

    def _rename_group(self):
        item = self.group_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择一个小组")
            return
        old_name = item.data(Qt.UserRole)
        new_name, ok = QInputDialog.getText(self, "重命名小组",
                                             f"将 '{old_name}' 重命名为:",
                                             text=old_name)
        if ok and new_name.strip():
            ok2, msg = dm.rename_group(old_name, new_name.strip())
            if ok2:
                self.refresh()
            else:
                QMessageBox.warning(self, "提示", msg)
