from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit

from lt_conf import register_node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils_no_qt import dumpException
from nodes.node_base import BaseGraphicsNode, BaseNode


@register_node("INPUT")
class CalcNode_Input(BaseNode):
    icon = "icons/in.png"
    op_code = "INPUT"
    op_title = "Input"
    content_label_objname = "node_input"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])

    def evalImplementation(self):
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        return self.value
