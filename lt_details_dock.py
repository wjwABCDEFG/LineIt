from PySide6.QtWidgets import *


class LineItDetailsDock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        self.info_layout = QVBoxLayout()
        main_layout.addLayout(self.info_layout)
        main_layout.addStretch()

    def showDetailInfo(self, info: list['QWidget']):
        # 允许节点往details面板添加自己需要的可配置信息
        # 在qt中，只是想移除（界面），但并不想删除deleteLater子组件（下次可能还用），应该像这样解除绑定而不是删除
        # 另：在qt中，应该通过layout来操作变动，而不要重新创建layout再setLayout，没有效果的
        item = self.info_layout.takeAt(0)
        if item and item.widget():
            item.widget().setParent(None)

        for group in info:
            self.info_layout.addWidget(group)
