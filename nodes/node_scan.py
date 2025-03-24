# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import os
import time

from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import *

from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("SCAN_FILE")
class NodeScan(BaseNode):
    icon = "icons/file.png"
    op_code = "SCAN_FILE"
    op_title = "所有文件"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, inputs, outputs)
        self.ui_ext = None
        self.ui_path = None
        self.createDetailsInfo()

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('Params')
        group_layout = QVBoxLayout(group)

        # filepath行
        file_layout = QHBoxLayout()
        label = QLabel("FilePath")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.ui_path = QLineEdit()
        file_layout.addWidget(label)
        file_layout.addWidget(self.ui_path)
        group_layout.addLayout(file_layout)

        # 后缀过滤行
        ext_layout = QHBoxLayout()
        label = QLabel("后缀名(.xxx)")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.ui_ext = QLineEdit()
        ext_layout.addWidget(label)
        ext_layout.addWidget(self.ui_ext)
        group_layout.addLayout(ext_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        path = self.ui_path.text()
        res = os.listdir(path)
        if self.ui_ext.text():
            res = [os.path.join(path, i) for i in res if i.endswith(self.ui_ext.text())]
        return res

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):
        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = {
                'file_path': self.node.ui_path.text(),
                'ext': self.node.ui_ext.text()
            }
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.ui_path.setText(value['file_path'])
                self.node.ui_ext.setText(value['ext'])
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
