#!/bin/bash
# GameboyPi Einrichtung auf RetroPie 4.8 (Pi Zero 2 W). Auf dem Pi ausführen:
#   sudo bash install.sh
# Erwartet die Dateien dieses Ordners im selben Verzeichnis.
# Mehrfach ausführbar: bereits erledigte Schritte werden übersprungen.
set -euo pipefail
cd "$(dirname "$0")"
SRC="$PWD"

if [ "$(id -u)" -ne 0 ]; then
    echo "Bitte mit sudo ausführen: sudo bash install.sh" >&2
    exit 1
fi

# config.txt nur einmal ergänzen (Marker gilt für v1.1 und v1.2)
if ! grep -q "===== GameboyPi v1" /boot/config.txt; then
    cp /boot/config.txt /boot/config.txt.vor-gameboypi
    cat config.txt.append >> /boot/config.txt
    echo "config.txt ergänzt (Sicherung: /boot/config.txt.vor-gameboypi)"
elif ! grep -q "^gpio=20=ip,pn" /boot/config.txt; then
    # Upgrade v1.1 -> v1.2: GPIO20 ohne internen Pull (R10 = 100k)
    printf '\n# GameboyPi v1.2: LBO-Eingang ohne internen Pull\ngpio=20=ip,pn\n' >> /boot/config.txt
    echo "config.txt: gpio=20=ip,pn nachgetragen"
fi

apt-get update
apt-get install -y cmake git python3-smbus python3-rpi.gpio

# Display-Treiber fbcp-ili9341 (DC=GPIO25, RST=GPIO24, SPI0 CE0)
# Pi Zero 2 W hat 4 Kerne -> KEIN -DSINGLE_CORE_BOARD. Bildfehler? Teiler 8 oder 10 probieren.
FBCP=/opt/fbcp-ili9341
if [ ! -x "$FBCP/build/fbcp-ili9341" ]; then
    [ -d "$FBCP/.git" ] || git clone https://github.com/juj/fbcp-ili9341.git "$FBCP"
    mkdir -p "$FBCP/build"
    cd "$FBCP/build"
    cmake -DILI9341=ON -DGPIO_TFT_DATA_CONTROL=25 -DGPIO_TFT_RESET_PIN=24 \
          -DSPI_BUS_CLOCK_DIVISOR=6 -DSTATISTICS=0 ..
    make -j2
    cd "$SRC"
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
