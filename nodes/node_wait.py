# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import time

from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import *

from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("WAIT_TIME")
class NodeWait(BaseNode):
    icon = "icons/wait.png"
    op_code = "WAIT_TIME"
    op_title = "等待"
    content_label_objname = "node_wait"   # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
        group = QGroupBox('Params')
        group_layout = QVBoxLayout(group)

        # 等待时间部分
        wait_layout = QHBoxLayout()
        label = QLabel("等待时间(s)")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.ui_wait_time = QLineEdit()
        self.ui_wait_time.textChanged.connect(self.updateLabelText)
        wait_layout.addWidget(label)
        wait_layout.addWidget(self.ui_wait_time)

        group_layout.addLayout(wait_layout)

        self.detailsInfo.append(group)

    def updateLabelText(self, obj:str):
        try:
            float(obj)
            self.title = f"等待{obj}s"
            self.markInvalid(False)
            self.grNode.setToolTip("时间参数必须是数字类型")
        except ValueError:
            self.markInvalid(True)

    def evalOperation(self, *args):
        sec = float(self.ui_wait_time.text())
        time.sleep(sec)
        # 该节点会保留对父节点的value，这样对后续节点就好像除了延迟什么都没变化一样
        return self.getInput(0).value

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):
        def initUI(self):
            pass

        def enterEvent(self, event):
            if self.node.isInvalid():
                # 显示提示文本（在光标位置右侧显示）
                QToolTip.showText(
                    QCursor.pos() + QPoint(10, 0),  # 提示位置偏移
                    "时间参数必须是数字类型",
                    self,
                    QRect(),  # 无关联控件区域
                    2000  # 提示显示时间（毫秒）
                )

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.ui_wait_time.text()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.ui_wait_time.setText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
