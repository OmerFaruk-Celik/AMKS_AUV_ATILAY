### 1.2 Simülasyonlar ve Deneysel Sonuçlar

#### 1.2.1 Uygulama Sonuçları ve Kullanılan Veri Setleri

Bu çalışmada, çeşitli donanım ve yazılım bileşenleri kullanılarak simülasyon ve deneysel sonuçlar elde edilmiştir.

**Donanım:**
- Bilgisayar özellikleri:
  - İşlemci: Intel(R) Core(TM) i3-1005G1 CPU @ 1.20GHz
  - Çekirdek Sayısı: 4
  - Bellek: 8 GB RAM
  - Mimari: x86_64
  - Maksimum İşlemci Hızı: 3.4 GHz

**Yazılım:**
- İşletim Sistemi: Ubuntu 22.04
- Python Sürümü: Python 3.11
- Kullanılan Kütüphaneler: Matplotlib, Numpy, Ursina, Sound
- IDE: Jupyter Notebook

Bu çalışmada, dalga ve su altı simülasyonları için Ursina kütüphanesi, veri görselleştirme için Matplotlib ve Numpy kütüphaneleri kullanılmıştır. Yazılımsal testlerde, 8-16 bit arası veri yollama işlemleri gerçekleştirilmiştir.

**Şekil 1**: Donanım ve Yazılım Yapılandırması. Bu şekil, kullanılan bilgisayar donanımının ve yazılım ortamının özelliklerini göstermektedir. Bilgisayarın işlemci yapısı, çekirdek sayısı, bellek kapasitesi ve kullanılan yazılım araçları detaylı bir şekilde sunulmuştur.

##### 1.2.1.1 STM32F103C

Bu çalışmada STM32F103C mikrokontrolörü kullanılmıştır. STM32F103C'nin temel özellikleri şunlardır:

- ARM Cortex-M3 çekirdeği
- 72 MHz saat hızı
- 64 KB Flash hafıza
- 20 KB SRAM
- Çeşitli haberleşme protokolleri (SPI, I2C, USART)

##### 1.2.1.2 Kullanılan Özellikler

###### 1.2.1.2.1 Input Capture

STM32F103C'nin Input Capture özelliği kullanılarak frekans tespiti yapılmıştır.

###### 1.2.1.2.2 Timerlar

Çeşitli Timer özellikleri kullanılarak zamanlama ve frekans ölçümleri gerçekleştirilmiştir.

###### 1.2.1.2.3 PWM Üretme

PWM pini ile 30-40 kHz frekansında dalgalar üretilmiş ve bu dalgalar çıkışta 40 kHz'lik ultrasonik vericilere gönderilmiştir.

##### 1.2.1.3 Filtre Yapımı

###### 1.2.1.3.1 Kondansatörler

Bant geçiren filtre yapımı için 100uF ile 1nF arasında mercimek kondansatörler ve kutuplu kondansatörler kullanılmıştır. Bu kondansatörler, sinyalin belirli bir frekans aralığında geçirilmesini ve diğer frekansların bastırılmasını sağlamaktadır.

##### 1.2.1.4 Transistör ve Op-Amp Kullanımı

###### 1.2.1.4.1 Transistör

Deneylerde BC237 transistörü kullanılmıştır.

###### 1.2.1.4.2 Op-Amp

Op-amp olarak TL084CN ve LM741 modelleri kullanılmıştır. TL084CN, içinde 4 adet op-amp bulunan bir entegre devredir. LM741 op-amp'ı kare dalga üretmek için kullanılmıştır. Alıcı devresinde, Şekil 8'de gösterilen bant geçiren filtrelerle op-amp'lar kullanılarak sinyal 400 kat artırılmıştır. Bu sinyal, Şekil 9'da gösterilen kare dalga çevirici ile kare dalgaya çevrilerek STM32F103C'ye gönderilmiştir.

**Şekil 8**: Bant Geçiren Filtre. Bu şekil, bant geçiren filtre devresini göstermektedir. Sinyal, filtreler aracılığıyla 400 kat artırılmıştır.

**Şekil 9**: Kare Dalga Çevirici. Bu şekil, bant geçiren filtreler tarafından artırılan sinyalin kare dalgaya çevrildiği devreyi göstermektedir.

##### 1.2.1.5 Ultrasonik Transdüserler

###### 1.2.1.5.1 Verici

Verici olarak bir tane daha STM32F103C modeli kullanılarak PWM pini ile 30-40 kHz dalgalar üretilmiş ve bu dalgalar çıkışta 40 kHz'lik ultrasonik transdüserlere gönderilmiştir.

###### 1.2.1.5.2 Alıcı

Alıcı olarak aynı şekilde 40 kHz'lik bir ultrasonik transdüser kullanılmıştır. Donanım sınırlamaları nedeniyle, alıcıda normalde iki farklı frekansı algılayan ultrasonik transdüser olması gerekirken, deneyde bir tane kullanılmıştır. Bu deneyde 37 kHz frekansı 0'ları simgelerken, 38 kHz frekansı 1'leri simgelemektedir.

##### 1.2.1.6 Veri Görselleştirme

###### 1.2.1.6.1 LCD Ekran

Veriyi görselleştirmek için 16x2 LCD ekran kullanılmıştır. Bu LCD ekranın bazı önemli özellikleri şunlardır:

- 16 sütun ve 2 satırdan oluşmaktadır.
- HD44780 uyumlu kontrolör ile çalışmaktadır.
- Arka aydınlatma özelliği bulunmaktadır.
- 4-bit veya 8-bit veri yolu ile çalışabilmektedir.

Bu LCD ekranın 4-bit modu ile kullanılmasının nedeni, daha az veri yolu pini kullanarak mikrodenetleyicinin diğer pinlerini başka işlevler için serbest bırakmaktır. Bu sayede daha karmaşık devre tasarımlarında pin tasarrufu sağlanmaktadır.

**Şekil 10**: 16x2 LCD Ekran. Bu şekil, çalışmada kullanılan 16x2 LCD ekranın yapısını ve özelliklerini göstermektedir. Ekran, verilerin görselleştirilmesi için kullanılmıştır.

#### 1.2.2 Simülasyon Yol Şeması ve Veri Görselleştirme

Bu bölümde, simülasyon yol şeması ve veri görselleştirme süreçleri ele alınmıştır. Simülasyon yol şeması, simülasyon adımlarının görsel bir temsilidir. Veri görselleştirme için performans grafiği, sinüs artış grafiği ve kare dalga dönüşüm grafikleri sunulmuştur.

**Şekil 2**: Simülasyon Yol Şeması. Bu şekil, simülasyon sürecinin adımlarını ve bu adımların izlenme sırasını göstermektedir.

**Şekil 3**: Performans Grafiği. Bu şekil, çeşitli simülasyonlar ve deneyler sırasında elde edilen performans verilerini göstermektedir. Elde edilen veriler, sistemin etkinliğini ve verimliliğini değerlendirmek amacıyla incelenmiştir.

**Şekil 4**: Sinüs Artış Grafiği. Bu şekil, sinyalin zaman içindeki artışını ve sinüs dalgasının oluşumunu göstermektedir. Sinyalin nasıl şekillendiği ve zaman içindeki değişimi detaylı olarak sunulmuştur.

**Şekil 5**: Kare Dalga Dönüşüm Grafiği. Bu şekil, sinüs dalgalarının kare dalgalara dönüşüm sürecini göstermektedir. Sinyalin kare dalgaya dönüşümü sırasında meydana gelen değişiklikler ve bu değişikliklerin etkileri incelenmiştir.

Veri görselleştirme süreci, 2D ve 3D grafikler kullanılarak gerçekleştirilmiştir. Python kullanılarak denklem 6'nın 2 boyutlu, 3 boyutlu ve 4 boyutlu uzay-zaman testleri yapılmıştır.

**Şekil 6**: Denklem 6'nın 2 Boyutlu Grafik Gösterimi. Bu şekil, denklem 6'nın 2 boyutlu uzayda nasıl görselleştirildiğini göstermektedir. Denklem, belirli parametreler altında test edilerek görselleştirilmiştir.

**Şekil 7**: Denklem 6'nın 3 Boyutlu Grafik Gösterimi. Bu şekil, denklem 6'nın 3 boyutlu uzayda nasıl görselleştirildiğini göstermektedir. Denklem, üç boyutlu uzayda incelenerek elde edilen sonuçlar sunulmuştur.

**Şekil 8**: Denklem 6'nın 4 Boyutlu Grafik Gösterimi. Bu şekil, denklem 6'nın 4 boyutlu uzay-zaman içinde nasıl görselleştirildiğini göstermektedir. Denklem, dört boyutlu uzay-zaman içinde test edilerek elde edilen veriler görselleştirilmiştir.

#### 1.2.3 Karşılaştırma Sunumu

Bu bölümde, simülasyonlarda kullanılan hamming kodlama, gray kodlama ve Fourier ters Fourier serilerinin sonuçları karşılaştırılmıştır.

**Hamming ve Gray Kodlama:**
- Hataları azaltmak için kullanılmıştır.
  
**Şekil 9**: Hamming Kodlaması ile Elde Edilen Veri. Bu şekil, hamming kodlaması kullanılarak elde edilen veriyi göstermektedir. Hamming kodlaması, hataların tespit edilmesi ve düzeltilmesi için kullanılmıştır.

**Şekil 10**: Gray Kodlaması ile Elde Edilen Veri. Bu şekil, gray kodlaması kullanılarak elde edilen veriyi göstermektedir. Gray kodlaması, hataların azaltılması için kullanılmıştır.

**Fourier ve Ters Fourier Serileri:**
- Numpy kütüphanesi kullanılarak gerçekleştirilmiştir.
- Mikrofona yollanan ses dalgasının frekans spektrumunu çıkarmak ve demodüle etmek için kullanılmıştır.

**Şekil 11**: Fourier Dönüşümü ile Frekans Spektrumu. Bu şekil, Fourier dönüşümü kullanılarak elde edilen frekans spektrumunu göstermektedir. Ses dalgalarının frekans bileşenleri detaylı olarak incelenmiştir.

**Şekil 12**: Ters Fourier Dönüşümü ile Demodüle Edilmiş Sinyal. Bu şekil, ters Fourier dönüşümü kullanılarak elde edilen demodüle edilmiş sinyali göstermektedir. Demodülasyon sürecinin etkinliği ve doğruluğu değerlendirilmiştir.

**Şekil 13**: Hamming Kodlaması Olmadan Alınan Sonuçlar. Bu şekil, hamming kodlaması kullanılmadan elde edilen veriyi göstermektedir. Hamming kodlaması olmadan, hata oranlarının arttığı gözlemlenmiştir. Bu durum, veri iletiminde kodlamanın önemini vurgulamaktadır.

**Şekil 14**: Gray Kodlaması Olmadan Alınan Sonuçlar. Bu şekil, gray kodlaması kullanılmadan elde edilen veriyi göstermektedir. Gray kodlaması olmadan, hata oranlarının arttığı gözlemlenmiştir. Bu durum, hataların azaltılmasında gray kodlamanın etkisini göstermektedir.

**Şekil 15**: Hamming ve Gray Kodlaması ile Elde Edilen Veri. Bu şekil, hem hamming hem de gray kodlaması kullanılarak elde edilen veriyi göstermektedir. Her iki kodlama tekniği de kullanıldığında, hata oranlarının en düşük seviyede olduğu gözlemlenmiştir. Kodlama tekniklerinin birlikte kullanımı, veri iletiminde daha yüksek güvenilirlik sağlamaktadır.

Karşılaştırma faktörleri:
- Hata oranı
- Başarı oranı
- Frekansa bağlı iletim başarısı

**Şekil 16**: Frekansa Bağlı İletim Başarısı Grafiği. Bu şekil, farklı frekanslarda iletilen verilerin başarı oranlarını göstermektedir. Frekans arttıkça iletim performansının nasıl değiştiği ve kayıpların nasıl arttığı gözlemlenmiştir. Frekansın artışı ile birlikte veri iletim performansında düşüş gözlemlenmiştir.

Ayrıca, donanımsal olarak yapılan deneylerde ortam koşulları ve uzaklığa bağlı olarak performans kıyaslayan şekiller sunulmuştur.

**Şekil 17**: Ortam Koşullarına Bağlı Performans Grafiği. Bu şekil, farklı ortam koşullarında yapılan deneylerin performans sonuçlarını göstermektedir. Ortam koşulları değiştikçe iletim performansının nasıl etkilendiği gözlemlenmiştir. Örneğin, nemli ortamların iletim performansını olumsuz etkilediği görülmüştür.

**Şekil 18**: Uzaklığa Bağlı Performans Grafiği. Bu şekil, farklı uzaklıklarda yapılan deneylerin performans sonuçlarını göstermektedir. Mesafe arttıkça veri iletim performansının logaritmik olarak azaldığı gözlemlenmiştir. Bu durum, sesin enerjisinin mesafenin karesiyle doğru orantılı olarak azalmasından kaynaklanmaktadır. Mesafe arttıkça sinyal gücünün azalması, veri iletiminde daha fazla hata oranına sebep olmaktadır.

#### 1.2.4 Yorumlama ve Bilime Katkılar

Bu çalışmada elde edilen sonuçlar, bilime çeşitli katkılar sağlamaktadır. Özellikle, dalga ve su altı simülasyonları, frekans spektrum analizleri ve veri görselleştirme yöntemleri, ilgili alanlarda önemli bilgiler sunmaktadır.

Yapılan çalışmanın bilime sağladığı faydalar:
- Yeni simülasyon teknikleri geliştirilmiştir.
- Frekans spektrum analizlerinin uygulanabilirliği gösterilmiştir.
- Hamming ve gray kodlamanın hataları azaltma konusundaki etkisi ortaya konmuştur.

**Şekil 19**: Bilimsel Katkıların Görselleştirilmesi. Bu şekil, çalışmanın bilime olan katkılarını ve elde edilen bulguları görselleştirmektedir. Çalışmanın sonuçları, ilgili alanda yapılan diğer araştırmalar için referans niteliğindedir.

Bu makale, belirtilen başlıklar ve alt başlıklar altında, gerekli grafikler ve şekillerle zenginleştirilmiş bilimsel bir formatta sunulmuştur.
