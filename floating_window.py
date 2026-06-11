import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                              QHBoxLayout, QPushButton, QStackedWidget)
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QSettings
from PyQt5.QtGui import (QFont, QColor, QPainter, QBrush, QPen,
                          QPainterPath, QRegion, QCursor)

import data_manager as dm
from score_page import ScorePage
from group_page import GroupPage
from trend_page import TrendPage
from about import AboutPage


class SidebarItem(QWidget):
    """长条侧边栏项"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.selected = False
        self.hovered = False
        self.setFixedHeight(48)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧留出指示条空间
        spacer = QWidget()
        spacer.setFixedWidth(4)
        layout.addWidget(spacer)

        self.label = QLabel(text)
        self.label.setFont(QFont("Microsoft YaHei", 10))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #787d88;")

        layout.addWidget(self.label, stretch=1)

    def set_selected(self, sel):
        self.selected = sel
        if sel:
            self.label.setStyleSheet("color: #1e2026; font-weight: bold;")
        else:
            self.label.setStyleSheet("color: #787d88;")

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.hovered and not self.selected:
            painter.setBrush(QBrush(QColor(241, 243, 248)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect().adjusted(6, 3, -6, -3), 8, 8)
        painter.end()
        super().paintEvent(event)


class SidebarIndicator(QWidget):
    """侧边栏滑动指示条，用 pyqtProperty 驱动动画"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._indicator_y = 16.0
        self._anim = None

    def get_indicator_y(self):
        return self._indicator_y

    def set_indicator_y(self, y):
        self._indicator_y = y
        self.update()

    indicator_y = pyqtProperty(float, get_indicator_y, set_indicator_y)

    def move_to(self, y):
        self._anim = QPropertyAnimation(self, b"indicator_y")
        self._anim.setDuration(200)
        self._anim.setStartValue(self._indicator_y)
        self._anim.setEndValue(float(y))
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(80, 120, 240)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, self._indicator_y, 4, 36), 2, 2)


class TopBarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(32, 32)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                color: #aaaeb7;
                font: 13pt;
            }
            QPushButton:hover {
                color: #1e2026;
                background: #e8eaf0;
            }
        """)


class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_pos = None
        self.collapsed = False
        self.current_idx = 0
        self._edge_side = 'right'
        self._animating = False
        self._pre_collapse_geo = None
        self._settings = QSettings("Axlewire", "AxleScore")

        self._press_pos = None
        self._long_press_fired = False
        self._is_dragging = False
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.timeout.connect(self._on_long_press)

        # 初始化数据
        dm.init_data()

        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.expanded_w = 770 + 72 + 20 * 2
        self.expanded_h = 670 + 20 * 2
        self.collapsed_size = 44 + 20 * 2

        self.resize(self.expanded_w, self.expanded_h)

        # 恢复上次窗口位置
        pos = self._settings.value("window_pos", QPoint(800, 200))
        self.move(pos)

        #最外层
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(0)

        #顶部栏
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(52)
        self.top_bar.setStyleSheet("background: #fbfbfd;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(20, 0, 12, 0)

        top_label = QLabel("AxleScore")
        top_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        top_label.setStyleSheet("color: #1e2026;")

        self.top_sub = QLabel("  /  分数")
        self.top_sub.setFont(QFont("Microsoft YaHei", 11))
        self.top_sub.setStyleSheet("color: #aaaeb7;")

        top_layout.addWidget(top_label)
        top_layout.addWidget(self.top_sub)
        top_layout.addStretch()

        self.collapse_btn = TopBarButton("—")
        self.collapse_btn.clicked.connect(self.collapse)
        top_layout.addWidget(self.collapse_btn)

        self.close_btn = TopBarButton("×")
        self.close_btn.clicked.connect(QApplication.quit)
        top_layout.addWidget(self.close_btn)

        outer.addWidget(self.top_bar)

        #顶部栏分割线
        self.top_divider = QWidget()
        self.top_divider.setFixedHeight(1)
        self.top_divider.setStyleSheet("background: #ebedf1;")
        outer.addWidget(self.top_divider)

        #下方区域
        self.bottom_area = QWidget()
        self.bottom_area.setStyleSheet("background: #fbfbfd;")
        bottom_layout = QHBoxLayout(self.bottom_area)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        #侧边栏
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(72)
        self.sidebar.setStyleSheet("background: #f6f7f9;")
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(0, 16, 0, 16)
        side_layout.setSpacing(2)

        self.sidebar_items = []
        models_list, _ = dm.get_models()
        for i, name in enumerate(models_list):
            item = SidebarItem(name)
            item.mousePressEvent = lambda e, idx=i: self._on_sidebar(idx)
            self.sidebar_items.append(item)
            side_layout.addWidget(item)
            #补一个注释 这里的if判断是指在最后一个项目下不添加分割线。
            if i < len(models_list)-1:
                divider = QWidget()
                divider.setFixedHeight(1)
                divider.setFixedWidth(40)
                divider.setStyleSheet("background: #aaaeb7;")
                side_layout.addWidget(divider, alignment=Qt.AlignCenter)

        side_layout.addStretch()

        #滑动指示条
        self.sidebar_indicator = SidebarIndicator(self.sidebar)
        self.sidebar_indicator.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.sidebar_indicator.setGeometry(0, 0, 72, self.sidebar.height())

        bottom_layout.addWidget(self.sidebar)

        #侧边栏分割线
        side_div = QWidget()
        side_div.setFixedWidth(1)
        side_div.setStyleSheet("background: #ebedf1;")
        bottom_layout.addWidget(side_div)

        #内容
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #fbfbfd;")

        #页面
        self.score_page = ScorePage()
        self.group_page = GroupPage()
        self.trend_page = TrendPage()
        self.about_page = AboutPage()

        self.content_stack.addWidget(self.score_page)
        self.content_stack.addWidget(self.group_page)
        self.content_stack.addWidget(self.trend_page)
        self.content_stack.addWidget(self.about_page)

        bottom_layout.addWidget(self.content_stack, stretch=1)
        outer.addWidget(self.bottom_area, stretch=1)

        self.sidebar_items[0].set_selected(True)
        self.content_stack.setCurrentIndex(0)

        # 初始化刷新
        self.score_page.refresh()
        self.group_page.refresh()
        self.trend_page.refresh()

        #设置指示条初始位置
        QTimer.singleShot(50, self._init_indicator_pos)

    def _init_indicator_pos(self):
        if self.sidebar_items:
            item = self.sidebar_items[0]
            self.sidebar_indicator._indicator_y = float(item.y() + 6)
            self.sidebar_indicator.update()

    def _on_sidebar(self, idx):
        models_list, _ = dm.get_models()
        if idx == self.current_idx:
            return

        self.current_idx = idx
        for i, item in enumerate(self.sidebar_items):
            item.set_selected(i == idx)
        self.top_sub.setText(f"  /  {models_list[idx]}")

        # 滑动指示条到目标项
        target_item = self.sidebar_items[idx]
        indicator_y = target_item.y() + 6
        self.sidebar_indicator.move_to(indicator_y)

        # 直接切换页面
        self.content_stack.setCurrentIndex(idx)

        # 切换页面时刷新数据
        if idx == 0:
            self.score_page.refresh()
        elif idx == 1:
            self.group_page.refresh()
        elif idx == 2:
            self.trend_page.refresh()

    #收起
    def collapse(self):
        if self.collapsed or self._animating:
            return
        self._animating = True
        self.collapsed = True

        screen = QApplication.primaryScreen().geometry()
        center_x = self.x() + self.width() / 2
        self._edge_side = 'left' if center_x < screen.width() / 2 else 'right'
        self._pre_collapse_geo = self.geometry()

        self.top_bar.hide()
        self.top_divider.hide()
        self.bottom_area.hide()

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(280)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        cur = self.geometry()
        cs = self.collapsed_size
        cy = cur.y() + (cur.height() - cs) // 2
        if self._edge_side == 'left':
            target = QRect(0, cy, cs, cs)
        else:
            target = QRect(screen.width() - cs, cy, cs, cs)

        self._anim.setStartValue(cur)
        self._anim.setEndValue(target)
        self._anim.finished.connect(self._on_anim_done)
        self._anim.start()

    #展开
    def expand(self):
        if not self.collapsed or self._animating:
            return
        self._animating = True
        self.collapsed = False

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(280)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        cur = self.geometry()
        if self._pre_collapse_geo is not None:
            target = self._pre_collapse_geo
        else:
            screen = QApplication.primaryScreen().geometry()
            if self._edge_side == 'left':
                target = QRect(0, cur.y(), self.expanded_w, self.expanded_h)
            else:
                target = QRect(screen.width() - self.expanded_w, cur.y(),
                               self.expanded_w, self.expanded_h)

        self._anim.setStartValue(cur)
        self._anim.setEndValue(target)
        self._anim.finished.connect(self._on_expand_done)
        self._anim.start()

    def _on_anim_done(self):
        self._animating = False

    def _on_expand_done(self):
        self._animating = False
        self._press_pos = None
        self.drag_pos = None
        self.top_bar.show()
        self.top_divider.show()
        self.bottom_area.show()

    def _on_long_press(self):
        self._long_press_fired = True
        self._is_dragging = True
        self.setCursor(QCursor(Qt.ClosedHandCursor))

    #鼠标事件
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self.collapsed and not self._animating:
            self._press_pos = event.globalPos()
            self._drag_offset = event.globalPos() - self.pos()
            self._long_press_fired = False
            self._is_dragging = False
            self._long_press_timer.start(300)
            return
        self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return
        if self.collapsed:
            if self._press_pos is None:
                return
            dist = (event.globalPos() - self._press_pos).manhattanLength()
            if dist > 5 and not self._long_press_fired:
                self._long_press_timer.stop()
                self._long_press_fired = True
                self._is_dragging = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            if self._is_dragging:
                self.move(event.globalPos() - self._drag_offset)
            return
        if self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if self.collapsed:
            self._long_press_timer.stop()
            if not self._long_press_fired and not self._is_dragging:
                self.expand()
            elif self._is_dragging:
                self._snap_to_edge()
            self._long_press_fired = False
            self._is_dragging = False
            self._press_pos = None
            self.setCursor(QCursor(Qt.ArrowCursor))
            return
        self.drag_pos = None

    def _snap_to_edge(self):
        screen = QApplication.primaryScreen().geometry()
        center_x = self.x() + self.width() / 2
        self._edge_side = 'left' if center_x < screen.width() / 2 else 'right'

        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        cur_y = self.y()
        if self._edge_side == 'left':
            target = QPoint(0, cur_y)
        else:
            target = QPoint(screen.width() - self.collapsed_size, cur_y)

        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(target)
        self._anim.start()

    #绘制
    def _card_rect(self):
        m = 20
        return QRectF(m, m, self.width() - m * 2, self.height() - m * 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        card = self._card_rect()
        radius = 12

        #阴影
        for i in range(4):
            offset = 6 - i * 1.5
            r = card.adjusted(-offset, -offset + 2, offset, offset + 2)
            alpha = 8 + i * 8
            painter.setBrush(QBrush(QColor(60, 65, 80, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, radius + offset, radius + offset)

        # 卡片主体
        painter.setBrush(QBrush(QColor(251, 251, 253)))
        painter.setPen(QPen(QColor(230, 232, 236), 0.5))
        painter.drawRoundedRect(card, radius, radius)

        #收起状态
        if self.collapsed:
            painter.setPen(QPen(QColor(170, 174, 183), 2))
            cx = int(card.center().x())
            cy = int(card.center().y())
            if self._edge_side == 'right':
                painter.drawLine(cx + 4, cy - 6, cx - 3, cy)
                painter.drawLine(cx - 3, cy, cx + 4, cy + 6)
            else:
                painter.drawLine(cx - 4, cy - 6, cx + 3, cy)
                painter.drawLine(cx + 3, cy, cx - 4, cy + 6)
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        if hasattr(self, 'sidebar_indicator'):
            self.sidebar_indicator.setGeometry(0, 0, self.sidebar.width(), self.sidebar.height())

    def closeEvent(self, event):
        if not self.collapsed:
            self._settings.setValue("window_pos", self.pos())
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    window.move(800, 200)
    window.show()
    sys.exit(app.exec_())
