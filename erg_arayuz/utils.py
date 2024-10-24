import socket
from PyQt5.QtGui import QPixmap, QColor, QIcon, QPainter
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPixmap

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "IP alınamadı"

def draw_circle(color):
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, 20, 20)
    painter.end()
    return QIcon(pixmap)

def load_data_from_json(table):
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    def extract_percentage(toplam):
        try:
            # Yüzde değerini % işaretinden önceki kısmı alarak döndürüyoruz
            return float(toplam.split()[0].strip('%'))
        except ValueError:
            return 0

    # Hijyen yüzdesine göre büyükten küçüğe sıralama
    sorted_data = sorted(data["personel"], key=lambda x: extract_percentage(x["toplam"]), reverse=True)

    table.setRowCount(len(sorted_data))

    for row, personel in enumerate(sorted_data):
        isim = personel["isim"]
        
        # Sıralama sonucuna göre madalya ekleme
        if row == 0:
            isim = "🥇 " + isim
        elif row == 1:
            isim = "🥈 " + isim
        elif row == 2:
            isim = "🥉 " + isim

        toplam_orani = extract_percentage(personel["toplam"])
        
        # Hijyen yüzdesine göre renk seçimi
        if toplam_orani <= 20:
            icon = draw_circle('red')
        elif 21 <= toplam_orani <= 40:
            icon = draw_circle('orange')
        elif 41 <= toplam_orani <= 60:
            icon = draw_circle('yellow')
        elif 61 <= toplam_orani <= 80:
            icon = draw_circle('lightgreen')
        elif 81 <= toplam_orani <= 100:
            icon = draw_circle('green')
        else:
            icon = draw_circle('gray')

        # Verileri tabloya ekleme
        isim_item = QTableWidgetItem(icon, isim)
        table.setItem(row, 0, isim_item)
        table.setItem(row, 1, QTableWidgetItem(personel["meslek"]))
        table.setItem(row, 2, QTableWidgetItem(personel["hasta_alinma"]))
        table.setItem(row, 3, QTableWidgetItem(personel["hasta_cikma"]))
        table.setItem(row, 4, QTableWidgetItem(personel["toplam"]))
        table.setItem(row, 5, QTableWidgetItem(personel["dezenfektan"]))