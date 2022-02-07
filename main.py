import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt


def loadImg(ll, z, l, w=450, h=450):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&l={l}&z={z}&size={w},{h}"
    response = requests.get(map_request)

    if not response:
        text = "Запрос:\n"
        text += map_request + "\n"
        text += f"Http статус: {response.status_code} ({response.reason})"
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Ошибка выполнения запроса")
        msgbox.setIcon(QMessageBox.Icon.Critical)
        msgbox.setText(text)
        msgbox.exec()
        sys.exit(1)
    pixmap = QPixmap()
    pixmap.loadFromData(response.content)
    return pixmap


class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 10
        self.initUI()
        self.setImg()

    def initUI(self):
        self.setGeometry(300, 300, 482, 482)
        self.setWindowTitle('Большая задача по Maps API')

        self.label = QLabel(self)
        self.label.move(16, 16)
        self.label.resize(450, 450)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        if (e.key() == Qt.Key.Key_PageUp):
            self.z += 1
            self.z = min(self.z, 17)
            self.setImg()
        if (e.key() == Qt.Key.Key_PageDown):
            self.z -= 1
            self.z = max(self.z, 0)
            self.setImg()

    def setImg(self):
        self.pixmap = loadImg("37.530887,55.703118", self.z, "map")
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())
