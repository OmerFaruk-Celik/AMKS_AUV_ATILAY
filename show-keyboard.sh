#!/bin/bash

# Klavye uygulamasını başlat
matchbox-keyboard &

# Metin alanı aktif olduğunda klavyeyi göster
while true; do
    # Ekran klavyesi zaten açık mı?
    if ! pgrep -x "matchbox-keyboard" > /dev/null; then
        matchbox-keyboard &
    fi

    # 5 saniyede bir kontrol et
    sleep 5
done
