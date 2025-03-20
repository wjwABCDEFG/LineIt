# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from lt_conf import register_node
from lt_dev_mgr import dev_mgr
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
        self.createDetailsInfo()

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('Params')
        group_layout = QVBoxLayout(group)

        # 等待时间部分
        wait_layout = QHBoxLayout()
        label = QLabel("等待时间(s)")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.ui_wait_time = QLineEdit()
        wait_layout.addWidget(label)
        wait_layout.addWidget(self.ui_wait_time)

        group_layout.addLayout(wait_layout)

        self.detailsInfo.append(group)

    def evalImplementation(self, *args, **kwargs):
        # 该节点会保留对父节点的value，这样对后续节点就好像除了延迟什么都没变化一样
        self.value = self.getInput(0).value
        sec = float(self.ui_wait_time.text())
        time.sleep(sec)
        print(123)
        return self.value


    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):
        def initUI(self):
            pass

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
