import numpy as np
import pyaudio
import time

# Ses kayıt parametreleri
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Taşıyıcı frekansı
tasiyici_frekans = 5000

# PyAudio nesnesi oluştur
p = pyaudio.PyAudio()

# Çıkış akışını aç
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=CHUNK
)

# Gönderilecek veri (binary)
veri = np.array([1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=np.int16)
genisletilmis_veri = np.repeat(veri, CHUNK // len(veri))
print(genisletilmis_veri[:16])

# Taşıyıcı dalga oluşturma
t = np.arange(0, len(genisletilmis_veri)) / RATE
tasiyici_dalga = np.sin(2 * np.pi * tasiyici_frekans * t)
m=tasiyici_dalga * (genisletilmis_veri * 2 - 1) 
# Frekans modülasyonu
modüle_edilmis_dalga = m*32767 #np.where(m>0,m * 32767,m*-32767)

# Modüle edilmiş dalgayı ses cihazına gönderme
for i in range(10):
	stream.write(modüle_edilmis_dalga.astype(np.int16).tobytes())
	time.sleep(0.1)
# Akışı kapat
stream.stop_stream()
stream.close()
p.terminate()
