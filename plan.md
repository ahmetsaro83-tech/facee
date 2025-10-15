 Nihai Proje Mimarisi (PLAN.md)
Proje Amacı
Kullanıcının bir arayüz üzerinden TikTok linki girmesini, ayarları yapılandırmasını ve tek bir butona basarak videonun indirilip, Gemini ile zenginleştirilip, Facebook'ta paylaşılmasını sağlayan bir masaüstü uygulaması geliştirmek.

🛠️ Kullanılacak Teknolojiler
Dil: Python 3.x

GUI: PyQt5
Modern pytq5 arayüzlü olmalı

Web Otomasyonu: SeleniumBase

API İletişimi: Google Gemini API

Veri Saklama: JSON

📂 Güncellenmiş Modüler Dosya Yapısı
app.py: PyQt5 arayüzünü oluşturan ve çalıştıran ana uygulama dosyası. Tüm kullanıcı etkileşimleri burada yönetilir.

worker.py: Uzun süren otomasyon görevlerini (video indirme, yükleme vb.) arayüzü dondurmadan arka planda çalıştıran QThread sınıfını içerir.

config.py: API anahtarları, varsayılan yollar gibi ayarları içerir.

tiktok_scraper.py: TikTok veri çekme mantığını içerir.

video_downloader.py: Video indirme mantığını içerir.

data_manager.py: JSON veri yönetimi mantığını içerir.

gemini_handler.py: Gemini API iletişim mantığını içerir.

facebook_uploader.py: Facebook'a video yükleme mantığını içerir.

.cursorrules: Proje kurallarını belirtir.

to-do.md: Projenin geliştirme adımlarını içerir.

🌊 Arayüz Odaklı İş Akışı
Kullanıcı app.py'yi çalıştırır ve PyQt5 arayüzü açılır.

Kullanıcı, arayüzdeki alanlara TikTok linkini, Facebook bilgilerini ve diğer ayarları girer.

Kullanıcı "İşlemi Başlat" butonuna tıklar.

Buton, worker.py içindeki QThread'i tetikler. Bu, arayüzün donmasını engeller.

worker, sırasıyla tiktok_scraper, video_downloader, gemini_handler ve facebook_uploader modüllerini çağırır.

Her adımın ilerlemesi (örn: "Video indiriliyor...", "Facebook'a yükleniyor...") anlık olarak arayüzdeki bir "log" veya "durum" alanına yazdırılır.

İşlem tamamlandığında veya bir hata oluştuğunda kullanıcı arayüz üzerinden bilgilendirilir.

