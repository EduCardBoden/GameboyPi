#!/usr/bin/env python3
"""GameboyPi Akku-Überwachung.

* liest die Akkuspannung über den ADS1115 (AIN0 = VBAT / 2, I2C-Adresse 0x48)
* schreibt Spannung und Prozent nach /dev/shm/battery (für Overlays/Skripte)
* fährt sauber herunter, wenn der PowerBoost LBO meldet (GPIO20 low, Akku < 3,2 V)
  oder die gemessene Spannung 30 s lang unter SHUTDOWN_V liegt.

Benötigt: sudo apt install python3-smbus python3-rpi.gpio   (in RetroPie 4.8 vorhanden)
"""
import os
import subprocess
import time

import RPi.GPIO as GPIO
import smbus

ADS_ADDR = 0x48
LBO_GPIO = 20
SHUTDOWN_V = 3.30
DIVIDER = 2.0            # R11/R12 = 100k/100k
OUT = "/dev/shm/battery"

# Entladekurve LiPo (Ruhespannung -> Prozent), grob linear interpoliert
CURVE = [(4.20, 100), (4.05, 90), (3.95, 80), (3.87, 70), (3.81, 60), (3.77, 50),
         (3.73, 40), (3.69, 30), (3.65, 20), (3.55, 10), (3.40, 5), (3.30, 0)]


def read_vbat(bus):
    # Single-Shot, AIN0 gegen GND, PGA +-4,096 V, 128 SPS
    bus.write_i2c_block_data(ADS_ADDR, 0x01, [0xC3, 0x83])
    time.sleep(0.01)
    hi, lo = bus.read_i2c_block_data(ADS_ADDR, 0x00, 2)
    raw = (hi << 8) | lo
    if raw & 0x8000:
        raw -= 1 << 16
    return raw * 4.096 / 32768 * DIVIDER


def percent(v):
    if v >= CURVE[0][0]:
        return 100
    for (v1, p1), (v2, p2) in zip(CURVE, CURVE[1:]):
        if v >= v2:
            return round(p2 + (p1 - p2) * (v - v2) / (v1 - v2))
    return 0


def shutdown(reason):
    subprocess.call(["wall", "GameboyPi: %s - fahre herunter" % reason])
    time.sleep(3)
    subprocess.call(["systemctl", "poweroff"])


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LBO_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # R10 zieht zusätzlich hoch
    bus = smbus.SMBus(1)
    low_since = None
    avg = None
    while True:
        try:
            v = read_vbat(bus)
            avg = v if avg is None else avg * 0.8 + v * 0.2
            with open(OUT + ".tmp", "w") as f:
                f.write("%.2f %d\n" % (avg, percent(avg)))
            os.replace(OUT + ".tmp", OUT)
        except OSError:
            avg = None   # ADS1115 nicht erreichbar: nur LBO überwachen
        if GPIO.input(LBO_GPIO) == 0:
            shutdown("Akku leer (LBO)")
            return
        if avg is not None and avg < SHUTDOWN_V:
            low_since = low_since or time.time()
            if time.time() - low_since > 30:
                shutdown("Akku leer (%.2f V)" % avg)
                return
        else:
            low_since = None
        time.sleep(5)


if __name__ == "__main__":
    main()
