# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/17 16:53
@Author  : wenjiawei
"""
import requests
from PySide6.QtWidgets import *

from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseNode


@register_node("HTTP")
class NodeHTTP(BaseNode):
    icon = "icons/http.png"                # 这是图标
    op_title = "HTTP"                 # 这是title
    op_code = "HTTP"                     # 这是key，需要保持唯一
    content_label_objname = "node_http"  # 这是样式qss名称

    def __init__(self, scene, inputs=[2], outputs=[1]):      # 这里的inputs和outputs对应了socket的数量
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

        # method
        layout = QHBoxLayout()
        label = QLabel("method")
        self.request_method = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.request_method)
        group_layout.addLayout(layout)

        # url
        layout = QHBoxLayout()
        label = QLabel("URL")
        self.url = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.url)
        group_layout.addLayout(layout)

        # json
        layout = QHBoxLayout()
        label = QLabel("json")
        self.json = QPlainTextEdit()
        layout.addWidget(label)
        layout.addWidget(self.json)
        group_layout.addLayout(layout)

        # data
        layout = QHBoxLayout()
        label = QLabel("data")
        self.data = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.data)
        group_layout.addLayout(layout)

        # params
        layout = QHBoxLayout()
        label = QLabel("params")
        self.params = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.params)
        group_layout.addLayout(layout)

        # headers
        layout = QHBoxLayout()
        label = QLabel("headers")
        self.headers = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.headers)
        group_layout.addLayout(layout)

        # cookies
        layout = QHBoxLayout()
        label = QLabel("cookies")
        self.cookies = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.cookies)
        group_layout.addLayout(layout)

        group.setLayout(group_layout)
        self.detailsInfo.append(group)

    def evalOperation(self, *args):
        """
        节点eval时的操作
        :return: val，运行时return的值会成为该节点的value
        """
        resp = requests.Request(self.request_method.text(),
                                self.url.text(),
                                self.data.text(),
                                self.json.toPlainText(),
                                self.params.text(),
                                self.headers.text(),
                                self.cookies.text(),
                                self.files.text())
        return resp.json()

    # 重写Graph类的serialize/deserialize方法，这不是必要的，如果自定义了createDetailsInfo，且里面的数据需要保存文件时持久化才需要这这步
    class NodeInputContent(QDMNodeContentWidget):

        def initUI(self):
            pass

        def serialize(self):
            res = super().serialize()
            # res['value'] = self.node.edit_app_name.text()
            return res

        def deserialize(self, data, hashmap={}):
            res = super().deserialize(data, hashmap)
            try:
                value = data['value']
                # self.node.edit_app_name.setText(value)
                return True & res
            except Exception as e:
                dumpException(e)
            return res

    NodeContent_class = NodeInputContent
