from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QPixmap
from utils import get_ip_address, draw_circle, load_data_from_json
import subprocess
import platform  # İşletim sistemini tespit etmek için

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

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

# İşletim sistemi kontrolü yapılarak sinyal gücü alınır
# İşletim sistemi kontrolü yapılarak sinyal gücü alınır
def wifi_sinyal_gucu_al():
    try:
        os_name = platform.system()

        if os_name == "Linux":
            # Raspberry Pi üzerinde iwconfig komutunu kullanarak Wi-Fi sinyal gücünü al
            sonuc = subprocess.run(['iwconfig', 'wlan0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            wifi_bilgisi = sonuc.stdout.decode('utf-8')

            for satir in wifi_bilgisi.split('\n'):
                if "Link Quality" in satir:
                    # "Link Quality" satırını bulup sinyal gücünü çıkar
                    # Genellikle "Link Quality=30/70  Signal level=-65 dBm" gibi olur
                    signal_part = satir.split("Signal level=")[1]
                    signal_level = int(signal_part.split(' ')[0].replace('dBm', '').strip())
                    
                    # Wi-Fi sinyal gücünü yüzdeye çevirelim (örnek olarak -100 dBm ve -50 dBm aralığı alınabilir)
                    sinyal_yuzde = max(0, min(100, 2 * (signal_level + 100)))  # -100 dBm -> 0%, -50 dBm -> 100%
                    return sinyal_yuzde

        elif os_name == "Windows":
            # Windows için netsh komutunu kullan
            sonuc = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], stdout=subprocess.PIPE)
            wifi_bilgisi = sonuc.stdout.decode('utf-8')
            sinyal_satiri = [satir for satir in wifi_bilgisi.split('\n') if 'Signal' in satir]
            if sinyal_satiri:
                sinyal_gucu = int(sinyal_satiri[0].split(':')[1].strip().replace('%', ''))
                return sinyal_gucu

    except Exception as e:
        print(f"Hata: {e}")
    return None
