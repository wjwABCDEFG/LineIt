from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QLabel

from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils_no_qt import dumpException


DEBUG = False


class BaseGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 55
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class BaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class BaseNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "node_bg"   # 这是样式qss名称

    GraphicsNode_class = BaseGraphicsNode
    NodeContent_class = BaseNodeContent

    def __init__(self, scene, inputs=[2,2], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None       # 用于存储当前节点计算结果
        self.detailsInfo = []   # details面板显示的信息，必须是list[QWidget]

        self.markDirty()        # 一开始是dirty的，因为dirty才可以允许eval

    def initInnerClasses(self):     # AAA
        self.content = self.__class__.NodeContent_class(self)
        self.grNode = self.__class__.GraphicsNode_class(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalOperation(self, input1, input2):
        """
        需要子类实现，本来是重写evalImplementation的，但是重复固定代码太多了，又抽了一层
        input/output类还是实现evalImplementation无需实现这个
        """
        return 123

    def evalImplementation(self, *args, **kwargs):
        i1 = self.getInput(0)
        i2 = self.getInput(1)

        if i1 is None or i2 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(i1.eval(), i2.eval())
            self.value = val    # 计算完成，存入当前value，这是很重要的一步，下个节点就可以从这里拿值，也是一个cache
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()

            return val

    def eval(self, *args, **kwargs):
        """这是右键的eval操作，真正实现计算在evalImplementation"""
        if not self.isDirty() and not self.isInvalid():
            if DEBUG: print(" _> returning cached %s value:" % self.__class__.__name__, self.value)   # 如果已经是√状态就不再计算了，拿缓存
            return self.value

        try:
            val = self.evalImplementation(*args, **kwargs)
            return val
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))      # 值类型错误通过状态和悬浮提示来提示用户，不需要dumpException在控制台显示错误
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, socket=None):
        if DEBUG: print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        # self.eval()   # 这里不要连线自动计算了

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        if DEBUG: print("Deserialized CalcNode '%s'" % self.__class__.__name__, "res:", res)
        return res
