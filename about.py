from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QPushButton, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

STYLE = """
    QGroupBox {
        border: 1px solid #ebedf1;
        border-radius: 8px; margin-top: 12px;
        padding: 16px 12px 12px 12px;
        font-size: 12px; color: #787d88;
    }
    QGroupBox::title {
        subcontrol-origin: margin; left: 16px; padding: 0 6px;
    }
    QLabel { color: #1e2026; }
"""

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #fbfbfd;")
        self.init_ui()
        self.setFixedHeight(420)

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(24, 12, 24, 16)
        layout.setSpacing(12)

        # 标题
        title = QLabel("关于与设置")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e2026;")
        layout.addWidget(title)

        # 关于组
        about_box = QGroupBox("关于 AxleScore")
        about_box.setStyleSheet(STYLE)
        about_layout = QVBoxLayout(about_box)
        about_layout.addWidget(QLabel("版本：1.0.1"))
        about_layout.addWidget(QLabel("作者：Axlewire"))
        about_layout.addWidget(QLabel("许可：GPL v3"))
        about_layout.addWidget(QLabel("仓库：https://github.com/baizhou830/AxleScore"))
        layout.addWidget(about_box)

        # TODO：设置组
        settings_box = QGroupBox("设置项")
        settings_box.setStyleSheet(STYLE)
        settings_layout = QVBoxLayout(settings_box)
        settings_layout.addWidget(QLabel("设置施工中……"))
        layout.addWidget(settings_box)

