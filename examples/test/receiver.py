import pyaudio
import numpy as np
import struct
import matplotlib.pyplot as plt

# Mikrofon ayarları
RATE = 44100  # Örnekleme frekansı
CHUNK = 1024  # Her seferinde alınan veri miktarı

# Pyaudio nesnesi oluştur
p = pyaudio.PyAudio()

# Mikrofon girişi başlat
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Dinleme başlatıldı")

try:
    while True:
        # Veriyi oku
        data = stream.read(CHUNK)
        data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
        data_np = np.array(data_int, dtype='b')[::2] + 128
        
        # Fourier dönüşümünü uygula
        fft_data = np.fft.fft(data_np)
        freqs = np.fft.fftfreq(len(fft_data))

        # Frekansları hesapla
        freqs_in_hz = abs(freqs * RATE)
        
        # İlgili frekans aralığını filtrele
        idx = np.where((freqs_in_hz >= 15000) & (freqs_in_hz <= 18000))
        filtered_freqs = freqs_in_hz[idx]
        filtered_fft = np.abs(fft_data[idx])
        
        # En yüksek amplitüdü bul
        max_amplitude = np.max(filtered_fft)

        # Ekrana yaz
        print(f"15kHz - 18kHz Arasındaki Maksimum Amplitüd: {max_amplitude}")

except KeyboardInterrupt:
    print("Dinleme durduruldu")
    stream.stop_stream()
    stream.close()
    p.terminate()
