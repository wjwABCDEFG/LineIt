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


@register_node("LAUNCH_APP")
class NodeLaunch(BaseNode):
    icon = "icons/app.png"
    op_code = "LAUNCH_APP"
    op_title = "打开应用"
    content_label_objname = "node_launch"   # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):
        super().__init__(scene, inputs, outputs)
        self.edit_app_name = None
        self.createDetailsInfo()

    def createDetailsInfo(self):
        self.detailsInfo = []

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

    def evalOperation(self, *args):
        app_name = self.edit_app_name.text()

        i1 = self.getInput(0)
        devices = i1.value

        for dev in devices:
            dev_mgr.launchApp(dev, app_name)

        self.markDirty(False)
        self.markInvalid(False)
        self.grNode.setToolTip("")
        self.markDescendantsDirty()
        self.evalChildren()
        return self.value

    # 重写Graph类的serialize/deserialize方法
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            res['value'] = self.node.edit_app_name.text()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                self.node.edit_app_name.setText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
