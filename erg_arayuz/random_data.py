import json
import random
import time

# İsim ve meslek listelerini oluşturalım
isimler = ["Elif", "Ali", "Ayşe", "Murat", "Zeynep", "Emre", "Fatma", "Serkan", "Seda", "Yusuf", "Ahmet", "Gül", "Selin", "Kaan", "Leyla", "Orhan", "Merve", "Burak", "Aslı", "Ozan"]
meslekler = ["Doktor", "Hemşire", "Sağlık Teknikeri"]

# data.json dosyasını oku ve Python nesnesine dönüştür
def dosyadan_veri_oku(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as dosya:
        return json.load(dosya)

# Güncellenen verileri data.json dosyasına yaz
def dosyaya_veri_yaz(dosya_adi, veriler):
    with open(dosya_adi, "w", encoding="utf-8") as dosya:
        json.dump(veriler, dosya, indent=4, ensure_ascii=False)

# Verileri rastgele güncelleyen fonksiyon
def veri_guncelle(personel):
    random.shuffle(isimler)  # İsim listesini karıştır
    meslek_listesi = random.choices(meslekler, k=len(isimler))  # Her kişi için rastgele meslek seç
    for idx, p in enumerate(personel["personel"]):
        # İsim ve meslekleri sırayla seç
        p["isim"] = isimler[idx]
        p["meslek"] = meslek_listesi[idx]
        
        # Hasta alınma ve çıkma değerlerini gerçekçi aralıklarda rastgele üret
        hasta_alinma_yeni = random.randint(10, 50)
        hasta_cikma_yeni = random.randint(10, 50)
        toplam_yeni = hasta_alinma_yeni + hasta_cikma_yeni if hasta_alinma_yeni + hasta_cikma_yeni <= 100 else 100
        
        # Yeni değerleri yerleştir
        p["hasta_alinma"] = f"%{hasta_alinma_yeni} ({hasta_alinma_yeni}/20)"
        p["hasta_cikma"] = f"%{hasta_cikma_yeni} ({hasta_cikma_yeni}/20)"
        p["toplam"] = f"%{toplam_yeni} ({toplam_yeni}/40)"
        
        # Dezenfektan miktarını rastgele bir değer yapalım
        p["dezenfektan"] = str(random.randint(1, 20))
    
    return personel

# Sonsuz döngü ile her 20 saniyede bir veriyi güncelle ve kaydet
def veri_guncelleme_sureci(dosya_adi):
    while True:
        print("Veriler güncelleniyor...")
        
        # Dosyadan veriyi oku
        veriler = dosyadan_veri_oku(dosya_adi)
        
        # Verileri güncelle
        guncellenmis_veri = veri_guncelle(veriler)
        
        # Güncellenmiş verileri dosyaya yaz
        dosyaya_veri_yaz(dosya_adi, guncellenmis_veri)
        
        # 20 saniye bekle
        time.sleep(20)

# Programı çalıştır
veri_guncelleme_sureci("data.json")
