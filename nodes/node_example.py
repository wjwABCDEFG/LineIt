# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""

from PySide6.QtWidgets import *

from lt_conf import register_node
from nodes.node_base import BaseNode
from utils import throwException


# @register_node("EXAMPLE")                   # 放开这段注释，加了这个装饰器才会显示在左边节点列表中
class NodeExample(BaseNode):
    icon = "icons/store.png"                # 这是图标
    op_title = "EXAMPLE节点"                 # 这是title
    op_code = "EXAMPLE"                     # 这是key，需要保持唯一
    content_label_objname = "node_example"  # 这是样式qss名称

    def __init__(self, scene, inputs=[2, 1], outputs=[1]):      # 这里的inputs和outputs对应了socket的数量
        super().__init__(scene, inputs, outputs)

    def createDetailsInfo(self):
        """
        右边属性面板，这里可以允许用户自定义面板的参数，最后append到self.detailsInfo即可
        如果不需要，可以重写这个函数
        self.detailsInfo: list[QWidget]，是一个widget列表
        """
        super().createDetailsInfo()

        # details面板，自由发挥，最后append到detailsInfo即可
        group = QGroupBox('Params')
        group_layout = QVBoxLayout()

        # 每行label+edit
        app_layout = QHBoxLayout()
        label = QLabel("自定义属性")
        self.edit_app_name = QLineEdit()
        app_layout.addWidget(label)
        app_layout.addWidget(self.edit_app_name)
        group_layout.addLayout(app_layout)

        group.setLayout(group_layout)

        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        """
        节点eval时的操作
        :return: val，运行时return的值会成为该节点的value
        """
        app_name = self.edit_app_name.text()
        val = self.getInput(0).value        # getInput可以指定从input的第几个socket中取值
        return val

    # 重写serialize/deserialize方法不是必要的，如果自定义了createDetailsInfo，且里面的数据需要保存文件时持久化，那么需要
    @throwException
    def serialize(self):
        res = super().serialize()
        res['details_info']['app_name'] = self.edit_app_name.text()
        return res

    @throwException
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap)
        info = data['details_info']
        self.edit_app_name.setText(info['app_name'])
        return res
