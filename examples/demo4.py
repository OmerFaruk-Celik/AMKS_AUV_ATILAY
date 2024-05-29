import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import hilbert, butter, filtfilt
import time
from pyldpc import make_ldpc, encode, decode, get_message
import noisereduce as nr  # noisereduce kütüphanesini ekle
# Ses kayıt parametreleri
CHUNK = 512* 1  # Her seferde alınacak örnek sayısı
FORMAT = pyaudio.paInt16  # Örnek formatı
CHANNELS = 1  # Kanal sayısı
RATE = 44100  # Örnekleme hızı

# PyAudio nesnesi oluştur
p = pyaudio.PyAudio()

# Giriş akışını aç (mikrofonu dinleme)
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Butterworth band-pass filtre tasarımı
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Bitleri çözmek için fonksiyon

    
def al(data):
	b_biti=[1,1,1]
	n = 32
	d_v = 4
	d_c = 8
	snr = 20
	H, G = make_ldpc(n, d_v, d_c, systematic=True, sparse=True)
	gruplar = [data[i:i+64] for i in range(0, len(data), 64)]
	ana_ort=np.abs(np.mean(data))
	ortalamalar =[]
	
	for grup in gruplar:
		ortalama=np.mean(grup)
		if ortalama <=0:
			ortalamalar.append(-1)
		else:
			ortalamalar.append(1)
	ortalamalar=np.array(ortalamalar)	
	#print(ortalamalar[0])	
	d = decode(H, ortalamalar, snr)
	x=get_message(G, d)
	
	if np.array_equal(b_biti, x[:3]):
		return x
			
	return None
	

def filtrele(data, esik):
    """Ses sinyalini şiddetine göre filtreler.

    Args:
        data: Ses verisi (NumPy dizisi).
        esik: Filtreleme için kullanılacak eşik değeri.

    Returns:
        Filtrelenmiş ses verisi (NumPy dizisi).
    """

    # Eşik değerinden düşük olan örnekleri sıfırlar
    filtered_data = np.where(np.abs(data) > esik, data, 0)
    return filtered_data

# Frekans aralığı
lowcut = 1000.0
highcut = 22000.0

# Grafik hazırlıkları
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(-1000, 1000)
ax.set_xlim(0, CHUNK)
plt.xlabel('Zaman')
plt.ylabel('Genlik')
plt.title('Osiloskop')

# Frekans değeri için metin ekleyin
text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
text2 = ax.text(0.4, 0.9, '', transform=ax.transAxes)

# Mesaj için metin ekleyin
message_text = ax.text(0.05, 0.85, '', transform=ax.transAxes)




def parca_kontrol(s, sutun_sayisi, rate):
  """
  Verilen 's' verisini 'sutun_sayisi' kadar parçaya bölerek, her bir parçanın içindeki frekansı hesaplar.
  Eğer parçanın frekansı ortalama frekanstan büyükse 1, değilse 0 değerini döndüren bir dizi oluşturur.

  Args:
    s: Kontrol edilecek verilerin numpy dizisi.
    sutun_sayisi: Verinin bölüneceği parça sayısı.
    rate: Örnekleme oranı (Hz).

  Returns:
    Her bir parçanın frekans kontrol sonucunu (1: büyük, 0: küçük) gösteren bir numpy dizisi.
  """

  frekanslar=[]
  sutun_genisligi = len(s) / sutun_sayisi
  ortalama_frekans = 0

  for i in range(sutun_sayisi):
    baslangic_indeksi = int(i * sutun_genisligi)
    bitis_indeksi = int((i + 1) * sutun_genisligi)

    parca = s[baslangic_indeksi:bitis_indeksi]

    # Parçanın frekans spektrumunu hesaplama
    frekans = np.fft.rfftfreq(len(parca), 1/rate)
    spektrum = np.fft.rfft(parca)
    frekans_peak = frekans[np.argmax(np.abs(spektrum))]

    # Ortalama frekansı hesaplama
    ortalama_frekans += frekans_peak
    frekanslar.append(frekans_peak)
  ortalama_frekans=ortalama_frekans/16
  frekanslar=np.array(frekanslar)
  print(frekanslar)
  kosul1=frekanslar>17900
  kosul2=frekanslar<17930
  sonuc=kosul1 & kosul2
  
  bits=np.where(sonuc,1,0)

  return bits


def update_frame(frame):
    # Ses verilerini oku
    baslama_zamani = time.time()
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = np.frombuffer(data, dtype=np.int16)
    bitme_zamani = time.time()
    gecen_sure = bitme_zamani - baslama_zamani


    
    # Frekans spektrumunu hesapla
    frekans = np.fft.rfftfreq(len(data_int), 1/RATE)
    spektrum = np.fft.rfft(data_int)
    frekans_peak = frekans[np.argmax(np.abs(spektrum))]


    # Eğer frekans koşulu sağlanıyorsa:
    if frekans_peak > lowcut and frekans_peak < highcut:
        # Veriyi işleme ve grafiğe gönderme işlemlerini yap
        # Band-pass filtre uygulama
        n = 15  # the larger n is, the smoother curve will be
        b = [1.0 / n] * n
        a = 1
        yy = lfilter(b, a, data_int)
        filtered_data=yy
        
        

        
        
        
        #genis_veri = (data_int / tasiyici_dalga + 1) / 2
        
        filtered_data = bandpass_filter(yy, lowcut, highcut, RATE, order=5)
        #filtered_data = nr.reduce_noise(y=data_int, sr=RATE) 
        #filtered_data=filtrele(filtered_data,20)
        #print(filtered_data[:3])
        #genis_veri = np.where(filtered_data <= 0, -1, 1)

        # Veriyi güncelle
        line.set_ydata(filtered_data )
        print(parca_kontrol(filtered_data , 16, 44100))

        # Frekans değerini güncelle
        text.set_text(f'Frekans: {frekans_peak:.2f} Hz')
        text2.set_text(f'Sure: {gecen_sure:.4f} ms')

        # Bitleri çözümle ve mesajı yazdır (bu kısım isterseniz burada)
        #demodulated_signal = hilbert(filtered_data).real
        #mesaj = bitleri_cozumle(demodulated_signal)
        #if mesaj is not None:
        #    message_text.set_text(f'Mesaj: {mesaj}')
        #else:
        #    message_text.set_text('Mesaj: None')

    # Aksi takdirde grafiği güncelleme
    else:
        #print(frekans_peak)		
        line.set_ydata(np.repeat(0, CHUNK)) # Grafiğe rastgele veri gönder (boş bırakmak için)
        text.set_text('Frekans: Dışı')
        text2.set_text(f'Sure: {gecen_sure:.4f} ms')

    return line, text, message_text

# Animasyonu başlat
ani = animation.FuncAnimation(fig, update_frame, interval=1, blit=True)

# Grafik gösterimi
plt.show()

# Akışı kapat ve kaynakları serbest bırak
stream.stop_stream()
stream.close()
p.terminate()
