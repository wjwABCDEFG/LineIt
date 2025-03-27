# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/19 23:10
@Author  : wenjiawei
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

import global_data
from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodes.node_base import BaseNode, BaseGraphicsNode


@register_node("STORE")
class NodeStore(BaseNode):
    icon = "icons/store.png"
    op_code = "STORE"
    op_title = "Store"

    def __init__(self, scene):
        self.ui_label = None
        super().__init__(scene, inputs=[1], outputs=[])

    def createDetailsInfo(self):
        self.detailsInfo = []

        group = QGroupBox('Params')
        group_layout = QVBoxLayout()

        app_layout = QVBoxLayout()
        self.ui_label = QLabel("存储的key，该key需要在节点的成员中")
        ui_key = QLineEdit()
        app_layout.addWidget(self.ui_label)
        app_layout.addWidget(ui_key)

        group_layout.addLayout(app_layout)
        group.setLayout(group_layout)

        self.detailsInfo.append(group)

    def evalImplementation(self):
        input_node = self.getInput(0)
        key = self.ui_label.text()
        setattr(global_data, key, getattr(input_node, key))
