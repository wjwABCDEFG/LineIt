import sys

from PySide6.QtWidgets import QApplication

from lt_window import LineItWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = LineItWindow()

    # 居中
    screen = app.primaryScreen()
    size = screen.size()
    width, height = size.width(), size.height()
    x = (width - wnd.width()) / 2
    y = (height - wnd.height()) / 2
    wnd.move(int(x), int(y))

    wnd.show()

    sys.exit(app.exec())
