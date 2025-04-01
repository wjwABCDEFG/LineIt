# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""

from PySide6.QtWidgets import *

from lt_conf import register_node
from lt_dev_mgr import dev_mgr
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


# @register_node("EXAMPLE")                   # 加了这个装饰器才会显示在左边节点列表中
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

    # 重写Graph类的serialize/deserialize方法，这不是必要的，如果自定义了createDetailsInfo，且里面的数据需要保存文件时持久化才需要这这步
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
