# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import os

from PySide6.QtWidgets import *

from lt_conf import register_node
from nodes.node_base import BaseNode
from utils import throwException


@register_node("RENAME")
class NodeRename(BaseNode):
    icon = "icons/rename.png"
    op_code = "RENAME"
    op_title = "序列化重命名"

    def __init__(self, scene, inputs=[2], outputs=[1]):
        self.ui_align0 = None
        self.ui_fmt = None
        self.ui_prefix = None
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        super().createDetailsInfo()
        group = QGroupBox('Params')
        group_layout = QVBoxLayout(group)

        # 前缀行
        prefix_layout = QHBoxLayout()
        label = QLabel("前缀")
        self.ui_prefix = QLineEdit()
        prefix_layout.addWidget(label)
        prefix_layout.addWidget(self.ui_prefix)
        group_layout.addLayout(prefix_layout)

        # 格式线行
        fmt_layout = QHBoxLayout()
        label = QLabel("格式线(_)")
        self.ui_fmt = QLineEdit()
        fmt_layout.addWidget(label)
        fmt_layout.addWidget(self.ui_fmt)
        group_layout.addLayout(fmt_layout)
        
        # 是否补齐前缀零行
        align0_layout = QHBoxLayout()
        label = QLabel("是否补齐前缀0")
        self.ui_align0 = QCheckBox()
        align0_layout.addWidget(label)
        align0_layout.addWidget(self.ui_align0)
        group_layout.addLayout(align0_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        i1 = self.getInput(0)
        align0 = self.ui_align0.isChecked()
        count = 0
        if align0:
            count = len(str(len(i1.value)))
        for idx, old_file in enumerate(i1.value):
            _, ext = os.path.splitext(old_file)
            if count > 0:
                idx = str(idx).zfill(count)
            new_file = os.path.join(os.path.dirname(old_file), f'{self.ui_prefix.text()}{self.ui_fmt.text()}{idx}{ext}')
            os.rename(old_file, new_file)
        return True

    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info'].update({
            'prefix': self.ui_prefix.text(),
            'fmt': self.ui_fmt.text()
        })
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        info = data['details_info']
        self.ui_prefix.setText(info['prefix'])
        self.ui_fmt.setText(info['fmt'])
        return res
