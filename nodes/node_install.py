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
from utils import throwException


@register_node("INSTALL_APP")
class NodeInstall(BaseNode):
    icon = "icons/install.png"
    op_code = "INSTALL_APP"
    op_title = "安装应用"
    content_label_objname = "node_install"   # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.app_path = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
        group = QGroupBox('Params')
        group_layout = QVBoxLayout()

        app_layout = QHBoxLayout()
        label = QLabel("apk绝对路径")
        label.setAlignment(Qt.AlignRight)  # 设置右对齐
        self.app_path = QLineEdit()
        app_layout.addWidget(label)
        app_layout.addWidget(self.app_path)

        group_layout.addLayout(app_layout)
        group.setLayout(group_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        app_name = self.app_path.text()
        dev = self.getInput(0).value
        dev_mgr.installApp(dev, app_name)
        return dev

    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info']['app_path'] = self.app_path.text()
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        value = data['details_info']['app_path']
        self.app_path.setText(value)
        return res
