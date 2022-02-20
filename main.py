import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox, QGroupBox, QHBoxLayout, QRadioButton
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt


def loadImg(ll: tuple[float, float], z: int, l: str, w=450, h=450):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll[0]},{ll[1]}&l={l}&z={z}&size={w},{h}"
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
        self.z = 13
        self.ll = [37.530887, 55.703118]
        self.initUI()
        self.setImg()

    def initUI(self):
        self.setGeometry(300, 300, 482, 520)
        self.setWindowTitle('Большая задача по Maps API')

        self.label = QLabel(self)
        self.label.move(16, 16)
        self.label.resize(450, 450)

        groupBox = QGroupBox(self)
        groupBox.setGeometry(10, 470, 461, 41)
        groupBox.setTitle("Вид карты")
        horizontalLayoutWidget = QWidget(groupBox)
        horizontalLayoutWidget.setGeometry(10, 10, 441, 31)
        horizontalLayout = QHBoxLayout(horizontalLayoutWidget)

        self.rb_map_map = QRadioButton(horizontalLayoutWidget)
        self.rb_map_map.setText("схема")
        self.rb_map_map.setChecked(True)
        self.rb_map_map.toggled.connect(self.setImg)
        horizontalLayout.addWidget(self.rb_map_map)

        self.rb_map_sat = QRadioButton(horizontalLayoutWidget)
        self.rb_map_sat.setText("спутник")
        self.rb_map_sat.toggled.connect(self.setImg)
        horizontalLayout.addWidget(self.rb_map_sat)

        self.rb_map_hyb = QRadioButton(horizontalLayoutWidget)
        self.rb_map_hyb.setText("гибрид")
        self.rb_map_hyb.toggled.connect(self.setImg)
        horizontalLayout.addWidget(self.rb_map_hyb)

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
        if (e.key() == Qt.Key.Key_Right):
            self.ll[0] += 0.0045 * 2 ** (17 - self.z)
            self.ll[0] = min(self.ll[0], 180)
            self.setImg()
        if (e.key() == Qt.Key.Key_Left):
            self.ll[0] -= 0.0045 * 2 ** (17 - self.z)
            self.ll[0] = max(self.ll[0], -180)
            self.setImg()
        if (e.key() == Qt.Key.Key_Up):
            self.ll[1] += 0.0025 * 2 ** (17 - self.z)
            self.ll[1] = min(self.ll[1], 85)
            self.setImg()
        if (e.key() == Qt.Key.Key_Down):
            self.ll[1] -= 0.0025 * 2 ** (17 - self.z)
            self.ll[1] = max(self.ll[1], -85)
            self.setImg()

    def setImg(self):
        mapType = "map"
        if (self.rb_map_sat.isChecked()):
            mapType = "sat"
        elif (self.rb_map_hyb.isChecked()):
            mapType = "sat,skl"
        self.pixmap = loadImg(self.ll, self.z, mapType)
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())
