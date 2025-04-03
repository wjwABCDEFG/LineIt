from lt_conf import register_node
from nodes.node_base import BaseNode


@register_node("INPUT")
class NodeInput(BaseNode):
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
