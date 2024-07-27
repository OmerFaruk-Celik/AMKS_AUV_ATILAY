import pyaudio

# PyAudio nesnesini başlat
p = pyaudio.PyAudio()

# Mevcut aygıtları listele
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    print(f"Device ID: {i} - {device_info['name']}")

p.terminate()
