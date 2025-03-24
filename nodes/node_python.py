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


@register_node("PYTHON")
class NodePython(BaseNode):
    icon = "icons/python.png"
    op_code = "PYTHON"
    op_title = "Python"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, inputs, outputs)
        self.edit_app_name = None
        self.createDetailsInfo()

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('PythonCode')
        group_layout = QVBoxLayout(group)

        self.ui_code = QPlainTextEdit()
        self.ui_code.setObjectName("myTextEdit")
        self.ui_code.setStyleSheet("QPlainTextEdit { color: white; }")
        group_layout.addWidget(self.ui_code)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        code = self.ui_code.toPlainText()
        exec(code)
        return self.value

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.ui_code.toPlainText()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.ui_code.setPlainText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
