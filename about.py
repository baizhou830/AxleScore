from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QListWidget, QListWidgetItem,
                              QMessageBox, QGroupBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

ACCENT_BTN_STYLE = """
    QPushButton {
        background: #5078f0; color: white; border: none;
        border-radius: 6px; padding: 6px 14px;
        font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #6090E8; }
"""

INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #ebedf1;
        border-radius: 6px; padding: 4px 8px;
        background: white; color: #1e2026; font-size: 12px;
    }
    QLineEdit:focus { border-color: #5078f0; }
"""

LABEL_STYLE = "color: #787d88; font-size: 32px;"

class AboutPage(QWidget):
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

        label = QLabel("关于页正在施工喵")
        label.setStyleSheet(LABEL_STYLE)
        add_row.addWidget(label)

        layout.addLayout(add_row)