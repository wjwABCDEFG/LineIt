# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from lt_conf import register_node
from lt_dev_mgr import dev_mgr
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("INSTALL_APP")
class NodeInstall(BaseNode):
    icon = "icons/install.png"
    op_code = "INSTALL_APP"
    op_title = "安装应用"
    content_label_objname = "node_install"   # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.edit_text = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('Params')
        group_layout = QVBoxLayout()

        app_layout = QHBoxLayout()
        label = QLabel("apk绝对路径")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.edit_text = QLineEdit()
        app_layout.addWidget(label)
        app_layout.addWidget(self.edit_text)

        group_layout.addLayout(app_layout)
        group.setLayout(group_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        app_name = self.edit_text.text()
        dev = self.getInput(0).value
        dev_mgr.installApp(dev, app_name)
        return dev

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.edit_text.text()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.edit_text.setText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
