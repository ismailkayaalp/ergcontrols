from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPixmap
from utils import get_ip_address, draw_circle, load_data_from_json
import subprocess
import platform  # İşletim sistemini tespit etmek için

import sqlite3  # SQLite modülü

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

        # SQLite veritabanına bağlantı
        self.conn = sqlite3.connect('application_logs.db')
        self.cursor = self.conn.cursor()

        # Log tablosunu oluştur (eğer yoksa)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                wifi_signal_strength TEXT
            )
        ''')
        self.conn.commit()

        # Ana etiket (Başlık)
        self.title_label = QLabel('ERG CONTROLS', self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #2B3A67;")

        # Personel raporu ve saat etiketleri için yatay layout
        header_layout = QHBoxLayout()

        # Personel raporu etiketi
        self.personel_label = QLabel("Personel Raporu", self)
        self.personel_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #2B3A67;")  
        header_layout.addWidget(self.personel_label)

        # Saat etiketi
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #2B3A67;")
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)

        # Wi-Fi sinyal gücü etiketi
        self.wifi_label = QLabel('Wi-Fi sinyal gücü: ')
        self.wifi_label.setStyleSheet("font-size: 20px; color: #2B3A67;")

        # IP etiketi
        self.ip_label = QLabel()
        self.ip_label.setStyleSheet("font-size: 20px; color: #2B3A67;")

        # Bilgi etiketleri için alt layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.wifi_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.ip_label)

        # Renk kodları açıklama için daireler ekle
        self.legend_layout = QVBoxLayout()
        self.legend_layout.setAlignment(Qt.AlignCenter)

        colors = [("Kırmızı", "red", "0-20%"),
                  ("Turuncu", "orange", "21-40%"),
                  ("Sarı", "yellow", "41-60%"),
                  ("Açık Yeşil", "lightgreen", "61-80%"),
                  ("Yeşil", "green", "81-100%")]

        color_layout = QHBoxLayout()
        for _, color, range_text in colors:
            circle_label = QLabel()
            circle_label.setPixmap(draw_circle(color).pixmap(20, 20))
            color_layout.addWidget(circle_label)
            color_layout.addWidget(QLabel(range_text))

        self.legend_layout.addLayout(color_layout)
        self.legend_layout.addWidget(QLabel("           Toplam el hijyen uyum oranına göre renklendirilmiştir."))

        # Tablo oluşturma
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PERSONEL ADI", 
            "MESLEK", 
            "HASTA ALANINA GİRİŞ ANI", 
            "HASTA ALANINDAN ÇIKIŞ ANI", 
            "TOPLAM",
            "DEZENFIKTAN KULLANIMI"
        ])

        self.table.setFont(QFont('Arial', 14))
        self.table.setStyleSheet("""
            QTableWidget { 
                font-size: 16px; 
                background-color: #f5f5f5; 
                alternate-background-color: #eaf2f8;
                color: #2B3A67; 
                gridline-color: #d3d3d3;
            }
            QTableWidget::item { 
                border: 1px solid #d3d3d3; 
                padding: 8px;
                text-align: center;
            }
            QTableWidget::item:selected { 
                background-color: #cce4ff; 
                color: #2B3A67;
            }
        """)

        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section { 
                background-color: #2B3A67; 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
                padding: 12px;
                text-align: center;
                border: 1px solid #d3d3d3;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(self.legend_layout)
        main_layout.addWidget(self.table)

        # Resim eklemek için QLabel
        self.image_label = QLabel(self)
        pixmap = QPixmap('image.png')
        scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.image_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('ERG Controls Information Screen')
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)
        
        self.page_timer = QTimer(self)
        self.page_timer.timeout.connect(self.change_page)
        self.page_timer.start(5000)  # 5 saniyede bir sayfa değiştir

        # Verileri güncellemek için yeni bir zamanlayıcı oluştur
        self.data_update_timer = QTimer(self)
        self.data_update_timer.timeout.connect(lambda: load_data_from_json(self.table))
        self.data_update_timer.start(20000)  # 20 saniyede bir tabloyu güncelle
        
        self.current_page = 0
        load_data_from_json(self.table)

        # Uygulama açıldığında log kaydet
        self.log_application_start()

    def update_info(self):
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.time_label.setText(f"Saat: {current_time}")

        ip_address = get_ip_address()
        self.ip_label.setText(f"IP: {ip_address}")

        # Wi-Fi sinyal gücünü al
        sinyal_gucu = wifi_sinyal_gucu_al()
        if sinyal_gucu is not None:
            if sinyal_gucu >= 75:
                sinyal_cubugu = "🟩🟩🟩🟩"
            elif sinyal_gucu >= 50:
                sinyal_cubugu = "🟩🟩🟩⬜"
            elif sinyal_gucu >= 25:
                sinyal_cubugu = "🟩🟩⬜⬜"
            else:
                sinyal_cubugu = "🟥⬜⬜⬜"
            self.wifi_label.setText(f'Wi-Fi sinyal gücü: {sinyal_cubugu}')

    def change_page(self):
        total_rows = self.table.rowCount()
        if total_rows <= 10:
            return  # Satır sayısı 10'dan az ise sayfa değiştirme

        max_rows_per_page = 10
        total_pages = (total_rows + max_rows_per_page - 1) // max_rows_per_page

        self.current_page = (self.current_page + 1) % total_pages
        start_row = self.current_page * max_rows_per_page
        end_row = start_row + max_rows_per_page

        for row in range(total_rows):
            self.table.setRowHidden(row, not (start_row <= row < end_row))

    def log_application_start(self):
        # Zaman damgası, IP adresi ve Wi-Fi sinyal gücü ile veritabanına log kaydet
        timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        ip_address = get_ip_address()
        sinyal_gucu = wifi_sinyal_gucu_al()

        self.cursor.execute('''
            INSERT INTO logs (timestamp, ip_address, wifi_signal_strength)
            VALUES (?, ?, ?)
        ''', (timestamp, ip_address, sinyal_gucu))
        self.conn.commit()

# İşletim sistemi kontrolü yapılarak sinyal gücü alınır
def wifi_sinyal_gucu_al():
    try:
        os_name = platform.system()

        if os_name == "Linux":
            # Raspberry Pi üzerinde iwconfig komutunu kullanarak Wi-Fi sinyal gücünü al
            sonuc = subprocess.check_output(["iwconfig"], universal_newlines=True)
            sinyal_gucu = None
            for satir in sonuc.split("\n"):
                if "Link Quality" in satir:
                    # Wi-Fi sinyal gücünü çıkar
                    sinyal_gucu = int(satir.split("=")[1].split("/")[0])
                    break
            return sinyal_gucu

        elif os_name == "Windows":
            # Windows üzerinde netsh komutunu kullanarak Wi-Fi sinyal gücünü al
            sonuc = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], universal_newlines=True)
            for satir in sonuc.split("\n"):
                if "Signal" in satir:
                    # Wi-Fi sinyal gücünü çıkar
                    sinyal_gucu = int(satir.split(":")[1].strip().replace("%", ""))
                    return sinyal_gucu
        else:
            return None

    except Exception as e:
        print(f"Wi-Fi sinyal gücü alınırken hata: {e}")
        return None
