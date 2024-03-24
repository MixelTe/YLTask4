import math
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QRadioButton, QLineEdit, QPushButton, QCheckBox, QTextEdit, QFrame
from PyQt5.QtGui import QPixmap, QKeyEvent, QFont, QMouseEvent
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


def getData(geocode):
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
            name = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            index = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_coodrinates = list(map(float, toponym_coodrinates.split(" ")))
            return toponym_coodrinates, name, index
        except Exception:
            return None, None, None
    else:
        return None, None, None


def rectPointIntersect(rect, point):
    return (
        rect[0] + rect[2] >= point[0] and
        point[0] >= rect[0] and
        rect[1] + rect[3] >= point[1] and
        point[1] >= rect[1]
    )


def findPlace(address_ll):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    _, name, _ = getData(address_ll)
    if (name is None):
        return []

    search_params = {
        "apikey": api_key,
        "lang": "ru_RU",
        "text": name,
        "type": "biz",
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        return []

    json_response = response.json()
    return json_response["features"]


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = list(map(float, a.split(",")))
    b_lon, b_lat = list(map(float, b.split(",")))

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 13
        self.ll = [37.530887, 55.703118]
        self.lastPlace = None
        self.points = []
        self.initUI()
        self.setImg()

    def initUI(self):
        self.setGeometry(300, 300, 482, 620)
        self.setFixedSize(482, 620)
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
        self.inp_search.setGeometry(10, 520, 461, 21)
        self.btn_search = QPushButton(self)
        self.btn_search.setGeometry(400, 590, 71, 21)
        self.btn_search.setText("Искать")
        self.btn_search.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_search.clicked.connect(self.search)
        self.btn_delete = QPushButton(self)
        self.btn_delete.setGeometry(10, 590, 191, 23)
        self.btn_delete.setText("Сброс поискового результата")
        self.btn_delete.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_delete.clicked.connect(self.delete)
        self.lbl_search = QTextEdit(self)
        self.lbl_search.setGeometry(10, 550, 461, 31)
        self.lbl_search.setReadOnly(True)
        self.lbl_search.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.lbl_search.setFrameShape(QFrame.NoFrame)
        self.cb_index = QCheckBox(self)
        self.cb_index.setGeometry(210, 590, 181, 21)
        font1 = QFont()
        font1.setPointSize(8)
        self.cb_index.setFont(font1)
        self.cb_index.setText("Показывать почтовый индекс")
        self.cb_index.stateChanged.connect(self.setPlaceText)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.inp_search.clearFocus()
        pos = (e.pos().x(), e.pos().y())
        rectS = self.label.size()
        rectP = self.label.pos()
        rect = (rectP.x(), rectP.y(), rectS.width(), rectS.height())
        if (rectPointIntersect(rect, pos)):
            x = pos[0] - rect[0]
            y = pos[1] - rect[1]
            mapW = 0.0045 * 2 ** (17 - self.z)
            mapH = 0.0025 * 2 ** (17 - self.z)
            relX = mapW / rect[2]
            relY = -mapH / rect[3]
            point = (
                self.ll[0] + relX * x - mapW / 2,
                self.ll[1] + relY * y + mapH / 2,
            )
            if (e.button() == Qt.MouseButton.LeftButton):
                self.search(point)
            if (e.button() == Qt.MouseButton.RightButton):
                orgs = findPlace(f"{point[0]},{point[1]}")
                for org in orgs:
                    org_point = "{0},{1}".format(*org["geometry"]["coordinates"])
                    if (lonlat_distance(org_point, f"{point[0]},{point[1]}") <= 50):
                        self.points = []
                        self.points.append(list(map(float, org_point.split(","))))
                        self.lastPlace = [org["properties"]["name"], org["properties"]["description"]]
                        self.setPlaceText()
                        self.setImg()
                        return

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

    def search(self, point=None):
        if (not point):
            coords, name, index = getData(self.inp_search.text())
        else:
            coords, name, index = getData(f"{point[0]},{point[1]}")
        if (not coords):
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Поиск объекта")
            msgbox.setIcon(QMessageBox.Icon.Information)
            msgbox.setText("Не удалось найти объект.")
            msgbox.exec()
            return
        if (not point):
            self.ll = coords
        self.lastPlace = (name, index)
        self.setPlaceText()
        self.points = []
        self.points.append(tuple(coords))
        self.inp_search.clearFocus()
        self.setImg()

    def setPlaceText(self):
        if (self.lastPlace is None):
            self.lbl_search.setText("")
            return
        text = self.lastPlace[0]
        if (self.cb_index.isChecked()):
            text += " (" + self.lastPlace[1] + ")"
        self.lbl_search.setText(text)

    def delete(self):
        if (len(self.points) == 0):
            return
        self.points.pop()
        self.lastPlace = None
        self.inp_search.setText("")
        self.setPlaceText()
        self.setImg()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec())
