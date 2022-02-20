import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QRadioButton, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont
from PyQt5.QtCore import Qt, QEvent


def loadImg(ll: tuple[float, float], z: int, l: str, pt=None, w=450, h=450):
    map_request = f"http://static-maps.yandex.ru/1.x/"
    params = {
        "ll": f"{ll[0]},{ll[1]}",
        "l": l,
        "z": z,
        "size": f"{w},{h}",
    }
    if (pt):
        params["pt"] = pt
    response = requests.get(map_request, params=params)

    if not response:
        text = "Запрос:\n"
        text += response.url + "\n"
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


def getCoords(geocode):
    geocoder_request = f"https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": geocode,
        "format": "json",
    }

    response = requests.get(geocoder_request, params=params)
    if response:
        try:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_coodrinates = list(map(float, toponym_coodrinates.split(" ")))
            return toponym_coodrinates
        except Exception:
            return None
    else:
        return None


class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 13
        self.ll = [37.530887, 55.703118]
        self.points = []
        self.initUI()
        self.setImg()

    def initUI(self):
        self.setGeometry(300, 300, 482, 550)
        self.setWindowTitle('Большая задача по Maps API')
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        self.label = QLabel(self)
        self.label.move(16, 16)
        self.label.resize(450, 450)
        self.label.setFocus()

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
        self.rb_map_map.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        horizontalLayout.addWidget(self.rb_map_map)

        self.rb_map_sat = QRadioButton(horizontalLayoutWidget)
        self.rb_map_sat.setText("спутник")
        self.rb_map_sat.toggled.connect(self.setImg)
        self.rb_map_sat.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        horizontalLayout.addWidget(self.rb_map_sat)

        self.rb_map_hyb = QRadioButton(horizontalLayoutWidget)
        self.rb_map_hyb.setText("гибрид")
        self.rb_map_hyb.toggled.connect(self.setImg)
        self.rb_map_hyb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        horizontalLayout.addWidget(self.rb_map_hyb)

        self.inp_search = QLineEdit(self)
        self.inp_search.setGeometry(10, 520, 371, 21)
        self.btn_search = QPushButton(self)
        self.btn_search.setGeometry(394, 520, 71, 21)
        self.btn_search.setText("Искать")
        self.btn_search.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_search.clicked.connect(self.search)

    def mousePressEvent(self, e) -> None:
        self.inp_search.clearFocus()

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        if (self.inp_search.hasFocus()):
            if (e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return):
                self.search()
            return
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

    def getMapType(self):
        if (self.rb_map_sat.isChecked()):
            return "sat"
        elif (self.rb_map_hyb.isChecked()):
            return "sat,skl"
        return "map"

    def setImg(self):
        pt = None
        if (len(self.points) > 0):
            pt = "~".join(f"{p[0]},{p[1]},pm2rdm" for p in self.points)
        self.pixmap = loadImg(self.ll, self.z, self.getMapType(), pt)
        self.label.setPixmap(self.pixmap)

    def search(self):
        coords = getCoords(self.inp_search.text())
        if (coords is None):
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Поиск объекта")
            msgbox.setIcon(QMessageBox.Icon.Information)
            msgbox.setText("Не удалось найти объект.")
            msgbox.exec()
            return
        self.ll = coords
        self.points.append(tuple(coords))
        self.inp_search.clearFocus()
        self.setImg()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())
