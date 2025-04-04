# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from lt_conf import register_node
from nodes.node_base import BaseNode
from utils import throwException


@register_node("SCAN_FILE")
class NodeScan(BaseNode):
    icon = "icons/file.png"
    op_code = "SCAN_FILE"
    op_title = "所有文件"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.ui_ext = None
        self.ui_path = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
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

    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info'].update({
            'file_path': self.ui_path.text(),
            'ext': self.ui_ext.text()
        })
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        info = data['details_info']
        self.ui_path.setText(info['file_path'])
        self.ui_ext.setText(info['ext'])
        return res
