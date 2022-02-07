import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap


def loadImg(ll, z, l, w=450, h=450):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&l={l}&z={z}&size={w},{h}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    pixmap = QPixmap()
    pixmap.loadFromData(response.content)
    return pixmap


class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 482, 482)
        self.setWindowTitle('Окно')

        self.pixmap = loadImg("37.530887,55.703118", 10, "map")
        self.label = QLabel(self)
        self.label.move(16, 16)
        self.label.resize(450, 450)
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())
