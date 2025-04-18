from PySide6.QtCore import QSize, Qt, QByteArray, QDataStream, QIODevice, QMimeData, QPoint
from PySide6.QtGui import QPixmap, QIcon, QDrag
from PySide6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem

from lt_conf import LISTBOX_MIMETYPE, LINEIT_NODES, get_class_from_opcode
from nodeeditor.utils_no_qt import dumpException


class LineItNodesList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()

    def addMyItems(self):
        keys = list(LINEIT_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)

    def addMyItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.UserRole))

            # qt的数据存储格式，类似于一个bytearray，可以把图片stream后使用移位推入bytearray中，需要的时候通过位运算相同的位数取出
            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeQString(op_code)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e: dumpException(e)
