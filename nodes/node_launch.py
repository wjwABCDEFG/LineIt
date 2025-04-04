# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from lt_conf import register_node
from utils.lt_dev_mgr import dev_mgr
from nodes.node_base import BaseNode
from utils.util_simple import throwException


@register_node("LAUNCH_APP")
class NodeLaunch(BaseNode):
    icon = "icons/launch.png"
    op_code = "LAUNCH_APP"
    op_title = "打开应用"
    content_label_objname = "node_launch"   # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.edit_app_name = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
        group = QGroupBox('Params')
        group_layout = QVBoxLayout()

        # app包名行
        app_layout = QHBoxLayout()
        label = QLabel("App包名")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.edit_app_name = QLineEdit()
        app_layout.addWidget(label)
        app_layout.addWidget(self.edit_app_name)
        group_layout.addLayout(app_layout)

        group.setLayout(group_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args) -> str:
        app_name = self.edit_app_name.text()

        dev = self.getInput(0).value
        dev_mgr.launchApp(dev, app_name)
        return dev

    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info']['app_name'] = self.edit_app_name.text()
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        value = data['details_info']['app_name']
        self.edit_app_name.setText(value)
        return res
