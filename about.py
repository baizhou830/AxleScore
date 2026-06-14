from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QPushButton, QLineEdit, QCheckBox,QMessageBox)
from PyQt5.QtCore import Qt
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow


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

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #fbfbfd;")
        self.init_ui()
        self.setFixedHeight(420)

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'refresh'):
            self.refresh()

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
        about_layout.addWidget(QLabel("AxleScore 轻量级课堂小组积分管理工具"))
        about_layout.addWidget(QLabel(" "))
        about_layout.addWidget(QLabel("版本：1.0.1"))
        about_layout.addWidget(QLabel("作者：Axlewire"))
        about_layout.addWidget(QLabel("许可证：GPL v3"))
        about_layout.addWidget(QLabel(" "))
        about_layout.addWidget(QLabel("仓库主页：https://github.com/baizhou830/AxleScore"))
        about_layout.addWidget(QLabel("反馈建议：直接提Issue"))
        layout.addWidget(about_box)


        # 设置组
        settings_box = QGroupBox("设置项")
        settings_box.setStyleSheet(STYLE)
        settings_layout = QVBoxLayout(settings_box)
        settings_layout.setSpacing(8)

        row = QHBoxLayout()
        row.addWidget(self._label("尝试使用 QVariantAnimation 步进优化替代 pyqtProperty 驱动（实验性）："))
        self.startup_btn = QPushButton("未启用")
        self.startup_btn.setStyleSheet(ACCENT_BTN_STYLE)
        self.startup_btn.clicked.connect(self.startup)
        row.addWidget(self.startup_btn)
        row.addStretch()
        settings_layout.addLayout(row)

        settings_layout.addStretch()
        layout.addWidget(settings_box)

    def startup(self):
        message = QMessageBox.question(self, "确认启用",
                                     f"确定要启用该实验选项吗？\n若发生错误，目前的程序无法正确地fallback至 pyqtProperty 驱动，进而导致崩溃或异常。\n且 QVariantAnimation 所带来的优化极其有限。",
                                     QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            message1 = QMessageBox.question(self, "再次警告",
                                     f"此实验性设置项可能会带来风险。可能导致 QVariantAnimation 与现有动画冲突，界面可能出现卡死或异常。",
                                     QMessageBox.Yes | QMessageBox.No)
            if message1 == QMessageBox.Yes:
                url = "https://www.bilibili.com/video/BV1UT42167xb"
                webbrowser.open(url)

        
        

    #样式
    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(STYLE)
        return lbl