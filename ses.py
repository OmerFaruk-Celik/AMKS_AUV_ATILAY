import numpy as np
import sounddevice as sd

# Dalga parametreleri
frequency = 20141  # Frekans, 18 kHz
duration = 15.0     # Süre, saniye cinsinden (örneğin, 2 saniye)
sampling_rate = 44100  # Örnekleme hızı (CD kalitesinde ses için 44100 Hz kullanılır)

# Zaman dizisi oluşturma
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# 18 kHz'lik sinüs dalgası oluşturma
waveform = 0.5 * np.sin(2 * np.pi * frequency * t)

# Dalga çalma
sd.play(waveform, samplerate=sampling_rate)
sd.wait()  # Çalma işleminin tamamlanmasını bekler
