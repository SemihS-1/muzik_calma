# El Hareketleri ve Gülümseme ile Müzik Kontrolü

![image](https://github.com/user-attachments/assets/b336480e-60e8-4b10-9a38-5b1f77daf50e)

Bu proje, bilgisayar kamerası aracılığıyla el hareketleri ve yüz ifadelerini kullanarak müzik kontrolü sağlayan bir Python uygulamasıdır. MediaPipe el izleme ve DeepFace duygu tanıma kütüphaneleri kullanılarak geliştirilmiştir.

## 🎵 Özellikler

- **El Hareketleri ile Müzik Seçimi**: Sağ elinizle kaldırdığınız parmak sayısına göre müzik seçimi yapabilirsiniz (1-5 arası)
- **El Hareketleri ile Ses Kontrolü**: Sol elinizin başparmak ve işaret parmağı arasındaki mesafeye göre müzik ses seviyesini ayarlayabilirsiniz
- **Gülümseme Kontrolü**: Gülümsediğinizde çalan müzik duraklar
- **Gerçek Zamanlı Görsel Geri Bildirim**: Parmak sayısı, ses seviyesi ve duygu durumu ekranda gösterilir

## 📋 Gereksinimler

- Python 3.7+
- OpenCV (cv2)
- MediaPipe
- NumPy
- PyGame
- DeepFace


## 🚀 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/username/muzik-caldirma.git
cd muzik-caldirma

Gerekli kütüphaneleri yükleyin:

bashpip install opencv-python mediapipe numpy pygame deepface

MP3 dosyalarınızı projenin ana dizinine ekleyin (en az 5 tane önerilir)
Uygulamayı çalıştırın:

bashpython muzik_caldirma.py
🎮 Kullanım Kılavuzu
Müzik Seçimi (Sol El)
Kameraya sağ elinizi gösterin ve kaldırdığınız parmak sayısına göre müzik değişecektir:

1 parmak: 1. müzik dosyası
2 parmak: 2. müzik dosyası
...
5 parmak: 5. müzik dosyası

Ses Kontrolü (Sağ El)
Sağ elinizin başparmak ve işaret parmağı arasındaki mesafeyi değiştirerek ses seviyesini ayarlayabilirsiniz:

Parmaklar birbirine yakın: Düşük ses
Parmaklar birbirinden uzak: Yüksek ses

Duraklat/Devam Et
Gülümsediğinizde çalan müzik duraklar. Parmak göstererek müziği tekrar başlatabilirsiniz.
📸 Ekran Görüntüleri
Show Image
📚 Teknik Detaylar

MediaPipe Hands: El izleme ve parmak algılama için kullanılmıştır
DeepFace: Yüz ifadelerini analiz ederek gülümseme tespiti yapar
PyGame Sound: MP3 dosyalarının çalınması ve ses kontrolü için kullanılmıştır
OpenCV: Kamera görüntüsü işleme ve görselleştirme için kullanılmıştır

🔧 Sorun Giderme

Kamera Erişim Hatası: Cihazınızın kamera erişim izinlerini kontrol edin
MediaPipe Hataları: El algılama için iyi aydınlatılmış bir ortam sağlayın
MP3 Dosya Hatası: Dosya adlarında özel karakter veya boşluk olmamalıdır
Duygu Algılama Sorunları: Yüzünüzün iyi aydınlatılmış ve kameraya dönük olduğundan emin olun

📝 Lisans
Bu proje MIT Lisansı altında lisanslanmıştır.
👏 Katkıda Bulunma

Bu projeyi fork edin
Kendi branch'inizi oluşturun (git checkout -b yeni-ozellik)
Değişikliklerinizi commit edin (git commit -m 'Yeni özellik eklendi')
Branch'inizi push edin (git push origin yeni-ozellik)
Pull Request oluşturun

🔗 İletişim
GitHub: github.com/username
