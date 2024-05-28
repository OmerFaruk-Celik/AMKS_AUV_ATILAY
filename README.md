# AMKS: Arttırılabilir Menzilli Konumlandırma Sistemi

## Giriş

Bu proje, sualtı araçları için, GPS sinyallerinin ulaşamadığı ortamlarda güvenli ve etkili bir konumlandırma sistemi olan **Arttırılabilir Menzilli Konumlandırma Sistemi (AMKS)**'nin geliştirilmesini hedeflemektedir. AMKS, sualtı konumlandırma alanındaki mevcut çözümlerin dezavantajlarını ele alarak, ses dalgaları tabanlı, uzun menzilli, taşınabilir ve maliyet etkin bir çözüm sunmayı amaçlamaktadır.

## Proje Hedefi: Su Altında GPS

AMKS, temel olarak, sualtı araçlarına GPS benzeri bir konumlandırma yeteneği kazandırmayı amaçlayan bir sistemdir. Bu, sualtı araçlarının konumlarını belirlemelerini, güvenli bir şekilde gezmelerini ve hatta acil durumlarda kurtarma operasyonlarını kolaylaştırmalarını sağlayacaktır.

## AMKS'nin Çalışma Prensibi

AMKS, sualtında ses dalgalarını kullanarak konum belirleme işlemini gerçekleştirir. Sistem, iki taşınabilir istasyondan oluşan bir yapıya sahiptir:

1. **Vericiler:** İki istasyon, aracın bıraktığı akustik vericilerdir. Bu vericiler, aracın boyutuna göre ölçeklendirilebilir ve istenilen konuma yerleştirilebilir.
2. **Alıcı:** Araç, vericilerden gelen sinyalleri alarak zaman bilgisini çıkarır.

**Zaman Kodlama:**

AMKS'nin en önemli özelliği, ses dalgalarına ikili sayılarla kodlanmış zaman bilgisini eklemesidir. Bu, aracın konumunu belirlemek için iki yönlü ölçüm gerektirmeyen tek yönlü bir sistem olmasını sağlar.

**Menzil Arttırıcı:**

Sistemin menzilini artırmak için, sualtında bir sinyal güçlendirici kullanılacaktır. Bu güçlendirici, vericilerden gelen ses dalgalarının genliğini artırarak daha uzak mesafelere ulaşmalarını sağlar.

**Yardım Modülü:**

Acil durumlarda, araç, yardım modülünü tetikleyerek su yüzeyine bir kapsül gönderir. Kapsül, GPS sinyalleri alarak aracın küresel konumunu belirler ve bu bilgi kurtarma ekiplerine iletilir.

## AMKS'nin Avantajları

* **Uzun Menzil:**  Sinyal güçlendirici sayesinde, AMKS geleneksel sistemlere göre daha uzun mesafelerde konum belirleme olanağı sağlar.
* **Taşınabilirlik:** İstasyonlar, aracın boyutuna uygun şekilde ölçeklendirilebilir ve istenilen konuma yerleştirilebilir.
* **Maliyet Etkinliği:**  AMKS, LBL, SBL ve USBL sistemlerine kıyasla daha düşük maliyetlidir.
* **Güvenlik:**  Aracın konumunu belirlemek için birden fazla istasyon ve iki yönlü ölçüm gerektirmez.
* **Gizlilik:**  AMKS, pasif sonar prensibiyle çalıştığı için aracın konumunu aktif olarak ifşa etmez.

## Projenin Önemi

AMKS, sualtı keşif, araştırma, kurtarma operasyonları ve denizaltı haritalama gibi çeşitli alanlarda kullanılabilir. Bu sistem, sualtı araçlarının güvenliğini artırırken, operasyonların maliyetini düşürerek ve verimliliğini artırarak deniz bilimleri ve mühendisliğine önemli katkılar sağlayabilir.

## Proje Aşamaları

* **Sinyal Tasarımı:**  Akustik dalgalar için en uygun frekans ve kare dalga sinyallerinin modellenmesi.
* **Sayısal Tasarım:**  Sonar alıcı ve verici devrelerinin sayısal tasarımının yapılması.
* **Simülasyon:**  Alıcı ve verici sisteminin Python veya C dili ile simülasyonu.
* **Menzil Arttırıcı ve Yardım Modülü Tasarımı:** Bu modüllerin sayısal tasarımının yapılması.
* **Sistem Entegrasyonu:**  Tüm sistemin test edilmesi ve grafik arayüzünün oluşturulması.
* **Deniz Denemeleri:** Sistemin gerçek dünya koşullarında test edilmesi.

## Resimler

![AMKS Sistem Şeması](images/amks_sistem_şeması.png)
![Sinyal Güçlendirici](images/sinyal_güclendirme.png)
![Yardım Modülü](images/yardim_modulu.png)

## Katkıda Bulunma

Projenin geliştirilmesine katkıda bulunmak isterseniz, lütfen [GitHub repo linki](https://github.com/OmerFaruk-Celik/AMKS_AUV_ATILAY) adresinden iletişime geçin.

## Lisans

Bu proje [Lisans Türü] lisansı altında yayınlanmıştır. 

## Teşekkür

Bu projeyi destekleyen TÜBİTAK'a ve projede çalışan tüm kişilere teşekkür ederiz. 
