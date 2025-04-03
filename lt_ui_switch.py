# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/3 20:56
ref to 'Ctr+Alt+Del': https://blog.csdn.net/leaf_of_maple/article/details/138269595
"""
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QPainter, QColor, QPaintEvent
from PySide6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):
    def __init__(
            self,
            width: int = 50,
            button_height: int = 22,
            bg_color: str = "#777",
            circle_color: str = "#000",
            active_color: str = "00BCff",

            # Change animations here: 按钮动画
            animation_curve=QEasingCurve.Custom
            # Change the Bouncing of Round Ball
    ):
        QCheckBox.__init__(self)

        # Set Detail Parameter: 设置详细数据
        self.setFixedSize(width, button_height)
        self.setCursor(Qt.PointingHandCursor)

        # Color
        self._bg_color = bg_color  # Background Color: 背景颜色
        self._circle_color = circle_color  # Circle Color: 圆圈颜色
        self._active_color = active_color  # Active Color: 选中颜色

        # Create Animation: 创建动画事件
        self._circle_to_border = 4  # Circle Border: 圆圈默认距边框位置
        self._circle_position = 4  # Circle position: 圆圈目前所处位置，由 Qt.Property 控制
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(animation_curve)

        # Duration of Button Transition: 按钮转换的持续时间
        self.animation.setDuration(100)

        # Connect State Changed
        self.stateChanged.connect(self.start_transition)
        self.setCheckState(Qt.CheckState.Checked)

    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos_x: int):
        self._circle_position = pos_x
        self.update()

    @property
    def _circle_diameter(self):
        return self.height() - (self._circle_to_border * 2)

    def start_transition(self, state: bool):
        """
        利用按钮状态改变来定义动画滑动
        Args:
            state: bool

        Returns:

        """
        # Stop animation
        self.animation.stop()
        if state:
            # Circle animation left to right
            _circle_position = self.height() - self._circle_to_border
            self.animation.setEndValue(self.width() - _circle_position)
        else:
            # Circle animation right to left
            self.animation.setEndValue(self._circle_to_border)

        # Start animation
        self.animation.start()

    def hitButton(self, pos: QPoint) -> bool:
        """
        设置 Nes 的命中区域
        Args:
            pos:

        Returns:

        """
        return self.contentsRect().contains(pos)

    def paintEvent(self, event: QPaintEvent) -> None:
        rect = QRect(0, 0, self.width(), self.height())
        painter = QPainter(self)
        # setting anti-aliasing
        painter.setRenderHint(QPainter.Antialiasing)
        # Unchecked
        if not self.isChecked():

            # SET Background for night mode here
            painter.setBrush((QColor("#D9D9D9")))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0,
                                    rect.width(),
                                    self.height(),
                                    self.height() / 2,
                                    self.height() / 2)
            # Set Circle here
            painter.setBrush(QColor("#3B3B3B"))
            painter.drawEllipse(self._circle_position,
                                self._circle_to_border,
                                self._circle_diameter,
                                self._circle_diameter)

        else:

            # SET Background for Day mode here
            painter.setBrush(QColor("#188DB1"))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0,
                                    rect.width(),
                                    self.height(),
                                    self.height() / 2,
                                    self.height() / 2)
            # Set Circle here
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawEllipse(self._circle_position,
                                self._circle_to_border,
                                self._circle_diameter,
                                self._circle_diameter)
