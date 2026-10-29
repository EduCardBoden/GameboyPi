#!/bin/bash
# GameboyPi Einrichtung auf RetroPie 4.8 (Pi Zero 2 W). Auf dem Pi ausführen:
#   sudo bash install.sh
# Erwartet die Dateien dieses Ordners im selben Verzeichnis.
set -e
cd "$(dirname "$0")"

if ! grep -q "GameboyPi v1.1" /boot/config.txt; then
    cp /boot/config.txt /boot/config.txt.vor-gameboypi
    cat config.txt.append >> /boot/config.txt
    echo "config.txt ergänzt (Sicherung: /boot/config.txt.vor-gameboypi)"
fi

apt-get update
apt-get install -y cmake git python3-smbus python3-rpi.gpio

# Display-Treiber fbcp-ili9341 (DC=GPIO25, RST=GPIO24, SPI0 CE0)
if [ ! -x /opt/fbcp-ili9341/build/fbcp-ili9341 ]; then
    git clone https://github.com/juj/fbcp-ili9341.git /opt/fbcp-ili9341
    mkdir -p /opt/fbcp-ili9341/build
    cd /opt/fbcp-ili9341/build
    cmake -DILI9341=ON -DGPIO_TFT_DATA_CONTROL=25 -DGPIO_TFT_RESET_PIN=24 \
          -DSPI_BUS_CLOCK_DIVISOR=6 -DSTATISTICS=0 ..
    make -j2
    cd - >/dev/null
fi
cat > /etc/systemd/system/fbcp-ili9341.service <<'EOF'
[Unit]
Description=fbcp-ili9341 SPI-Display
DefaultDependencies=no
After=local-fs.target

[Service]
ExecStart=/opt/fbcp-ili9341/build/fbcp-ili9341
Restart=always

[Install]
WantedBy=sysinit.target
EOF

# Akku-Überwachung
mkdir -p /opt/gameboypi
cp battery_monitor.py /opt/gameboypi/
cp gameboypi-battery.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable fbcp-ili9341.service gameboypi-battery.service
echo "Fertig. Neu starten mit: sudo reboot"
