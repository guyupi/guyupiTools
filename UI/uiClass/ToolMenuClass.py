import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtCore import Qt, QPoint, QRect, QTimer
from PySide2.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath


class SectorMenu(QWidget):
    """扇形菜单组件"""

    def __init__(self, parent=None):
        super(SectorMenu, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 菜单配置
        self.radius = 100  # 菜单半径
        self.sectors = []  # 扇形区域列表
        self.highlight_index = -1  # 当前高亮的扇形索引
        self.center = QPoint(0, 0)  # 圆心位置

        # 默认添加几个示例扇形
        self.add_sector("保存", QColor(76, 175, 80))  # 绿色
        self.add_sector("打开", QColor(33, 150, 243))  # 蓝色
        self.add_sector("删除", QColor(244, 67, 54))  # 红色
        self.add_sector("设置", QColor(156, 39, 176))  # 紫色
        self.add_sector("帮助", QColor(255, 193, 7))  # 黄色

        # 信号槽连接
        self.sector_actions = [lambda:  ("执行操作: {}".format(s)) for s in self.sectors]

    def add_sector(self, text, color):
        """添加扇形区域"""
        self.sectors.append({
            "text": text,
            "color": color,
            "start_angle": 0,  # 将在绘制时计算
            "span_angle": 360 / len(self.sectors) if self.sectors else 360
        })
        self._update_sector_angles()

    def _update_sector_angles(self):
        """更新所有扇形的角度"""
        count = len(self.sectors)
        if count == 0:
            return

        angle_per_sector = 360 / count
        for i, sector in enumerate(self.sectors):
            sector["start_angle"] = i * angle_per_sector
            sector["span_angle"] = angle_per_sector

    def show_at(self, pos):
        """在指定位置显示菜单"""
        self.center = pos
        # 设置窗口位置和大小
        rect = QRect(pos.x() - self.radius, pos.y() - self.radius,
                     self.radius * 2, self.radius * 2)
        self.setGeometry(rect)
        self.show()

    def paintEvent(self, event):
        """绘制扇形菜单"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景（透明）
        painter.fillRect(self.rect(), Qt.transparent)

        # 绘制每个扇形
        for i, sector in enumerate(self.sectors):
            # 高亮效果
            color = sector["color"]
            if i == self.highlight_index:
                highlight_color = color.lighter(120)  # 亮度增加20%
                painter.setBrush(QBrush(highlight_color))
            else:
                painter.setBrush(QBrush(color))

            # 绘制扇形
            start_angle = sector["start_angle"] * 16  # 角度转换为1/16度
            span_angle = sector["span_angle"] * 16
            painter.drawPie(self.rect().adjusted(10, 10, -10, -10),
                            start_angle, span_angle)

            # 绘制文本
            self._draw_sector_text(painter, i, sector)

        # 绘制中心圆
        center_radius = self.radius // 5
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(self.center, center_radius, center_radius)

    def _draw_sector_text(self, painter, index, sector):
        """在扇形区域内绘制文本"""
        painter.save()

        # 计算文本位置
        angle = sector["start_angle"] + sector["span_angle"] / 2
        angle_rad = angle * 3.14159 / 180.0

        # 文本位置（距离圆心约2/3半径处）
        text_radius = self.radius * 0.6
        text_x = self.center.x() + text_radius * 0.8 * 3.14159 / 180.0 * angle
        text_y = self.center.y() + text_radius * 0.8

        # 设置文本样式
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 10, QFont.Bold))

        # 绘制文本
        painter.drawText(text_x, text_y, sector["text"])

        painter.restore()

    def mouseMoveEvent(self, event):
        """鼠标移动事件，检测鼠标位于哪个扇形区域"""
        pos = event.pos()
        index = self._get_sector_at(pos)

        if index != self.highlight_index:
            self.highlight_index = index
            self.update()  # 重绘以显示高亮效果

    def mouseReleaseEvent(self, event):
        """鼠标释放事件，执行对应扇形区域的操作"""
        if event.button() == Qt.RightButton:
            pos = event.pos()
            index = self._get_sector_at(pos)

            if index >= 0 and index < len(self.sector_actions):
                self.sector_actions[index]()

            self.close()  # 关闭菜单

    def _get_sector_at(self, pos):
        """确定指定位置位于哪个扇形区域"""
        # 计算与圆心的距离
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # 如果超出半径范围，返回-1
        if distance > self.radius * 0.9 or distance < self.radius * 0.2:
            return -1

        # 计算角度（修正错误）
        angle = 0
        if dx != 0:
            angle = 180.0 * 3.14159 / 180.0 * angle
            if dx < 0:
                angle += 180
            else:
                if dy < 0:
                    angle += 360

        # 确定所在扇形
        for i, sector in enumerate(self.sectors):
            if sector["start_angle"] <= angle < sector["start_angle"] + sector["span_angle"]:
                return i

        return -1
