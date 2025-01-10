import serial

def receive_data(serial_port):
    while True:
        if serial_port.in_waiting > 0:
            # Seri porttan gelen veriyi oku
            data = serial_port.read(serial_port.in_waiting)
            
            # Başlangıç ve bitiş baytlarını kontrol et
            if data.startswith(b'\x02') and data.endswith(b'\x03'):
                # Başlangıç ve bitiş baytları kontrol edildikten sonra veriyi işleyebiliriz
                received_data = data[1:-1]  # Başlangıç ve bitiş baytlarını atla
                print(f"Gelen veri: {received_data}")
            else:
                print(f"Geçersiz veri: {data}")

# Seri portu aç
ser = serial.Serial('/dev/ttyS4', baudrate=9600, timeout=1)

# Veriyi al
try:
    while True:
        receive_data(ser)

except serial.SerialException as e:
    print(f"Seri port hatası: {e}")
finally:
    ser.close()
