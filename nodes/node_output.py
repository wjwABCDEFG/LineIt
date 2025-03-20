# from PySide6.QtCore import Qt
# from PySide6.QtWidgets import QLabel
#
# from lt_conf import register_node
# from nodeeditor.node_content_widget import QDMNodeContentWidget
# from nodes.node_base import BaseNode, BaseGraphicsNode
#
#
# class NodeOutputContent(QDMNodeContentWidget):
#     def initUI(self):
#         self.lbl = QLabel("42", self)
#         self.lbl.setAlignment(Qt.AlignLeft)
#         self.lbl.setObjectName(self.node.content_label_objname)
#
#
# @register_node("OUTPUT")
# class NodeOutput(BaseNode):
#     icon = "icons/out.png"
#     op_code = "OUTPUT"
#     op_title = "Output"
#     content_label_objname = "node_output"
#
#     def __init__(self, scene):
#         super().__init__(scene, inputs=[1], outputs=[])
#
#     def initInnerClasses(self):
#         self.content = NodeOutputContent(self)
#         self.grNode = BaseGraphicsNode(self)
#
#     def evalImplementation(self):
#         input_node = self.getInput(0)
#         if not input_node:
#             self.grNode.setToolTip("Input is not connected")
#             self.markInvalid()
#             return
#
#         val = input_node.eval()
#
#         if val is None:
#             self.grNode.setToolTip("Input is NaN")
#             self.markInvalid()
#             return
#
#         self.content.lbl.setText(str(val))
#         self.markInvalid(False)
#         self.markDirty(False)
#         self.grNode.setToolTip("")
#
#         return val
