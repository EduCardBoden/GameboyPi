#!/usr/bin/env python3
"""GameboyPi Akku-Überwachung (v1.2).

* liest die Akkuspannung über den ADS1115 (AIN0 = VBAT / 2, I2C-Adresse 0x48)
* schreibt Spannung und Prozent nach /dev/shm/battery (für Overlays/Skripte)
* fährt sauber herunter, wenn der PowerBoost LBO meldet (GPIO20 low, Akku < 3,2 V)
  oder die gemessene Spannung 30 s lang unter SHUTDOWN_V liegt.

Änderungen v1.2:
* Teilerfaktor berücksichtigt die Eingangsimpedanz des ADS1115 (6 MOhm, TI-Datenblatt),
  sonst misst er ~0,8 % zu wenig. Feinabgleich über VBAT_CAL (Multimeter an TP1).
* LBO wird entprellt (LBO_COUNT Messungen in Folge), damit ein kurzer Einbruch unter
  Last nicht sofort herunterfährt.
* GPIO20 ohne internen Pull-up: R10 (100k) zieht hoch, der LBO-Ausgang darf max. 100 uA ziehen.
* Hardware-Zugriffe nur in main(): die Rechenfunktionen sind ohne Pi testbar (software/tests).

Benötigt: sudo apt install python3-smbus python3-rpi.gpio   (in RetroPie 4.8 vorhanden)
"""
import os
import subprocess
import time

ADS_ADDR = 0x48
LBO_GPIO = 20
SHUTDOWN_V = 3.30
SHUTDOWN_DELAY_S = 30
LBO_COUNT = 3            # LBO muss 3 Messungen in Folge low sein (3 x 5 s)
INTERVAL_S = 5
OUT = "/dev/shm/battery"

R_TOP, R_BOTTOM = 100e3, 100e3   # R11 / R12
R_ADC = 6e6                      # ADS1115 Gleichtakt-Eingangsimpedanz bei FSR +-4,096 V (typ.)
VBAT_CAL = 1.000                 # Abgleich: Multimeter-Wert an TP1 / angezeigter Wert


def divider_factor(r_top=R_TOP, r_bottom=R_BOTTOM, r_adc=R_ADC):
    """VBAT / U(AIN0) mit Belastung des unteren Widerstands durch den ADC-Eingang."""
    r_low = 1.0 / (1.0 / r_bottom + 1.0 / r_adc)   # Parallelschaltung, r_adc = inf erlaubt
    return (r_top + r_low) / r_low


DIVIDER = divider_factor()       # = 2,0167


def raw_to_vbat(raw, cal=VBAT_CAL):
    """16-Bit-Rohwert (Zweierkomplement, FSR +-4,096 V) -> Akkuspannung in V."""
    if raw & 0x8000:
        raw -= 1 << 16
    return raw * 4.096 / 32768 * DIVIDER * cal


# Entladekurve LiPo (Ruhespannung -> Prozent), grob linear interpoliert
CURVE = [(4.20, 100), (4.05, 90), (3.95, 80), (3.87, 70), (3.81, 60), (3.77, 50),
         (3.73, 40), (3.69, 30), (3.65, 20), (3.55, 10), (3.40, 5), (3.30, 0)]


def percent(v):
    if v >= CURVE[0][0]:
        return 100
    for (v1, p1), (v2, p2) in zip(CURVE, CURVE[1:]):
        if v >= v2:
            return round(p2 + (p1 - p2) * (v - v2) / (v1 - v2))
    return 0


class Monitor:
    """Entscheidungslogik ohne Hardware. step() liefert None oder den Abschaltgrund."""

    def __init__(self):
        self.avg = None
        self.low_since = None
        self.lbo_hits = 0

    def step(self, v, lbo_low, now):
        if v is None:
            self.avg = None          # ADS1115 nicht erreichbar: nur LBO überwachen
        else:
            self.avg = v if self.avg is None else self.avg * 0.8 + v * 0.2
        self.lbo_hits = self.lbo_hits + 1 if lbo_low else 0
        if self.lbo_hits >= LBO_COUNT:
            return "Akku leer (LBO)"
        if self.avg is not None and self.avg < SHUTDOWN_V:
            if self.low_since is None:
                self.low_since = now
            if now - self.low_since > SHUTDOWN_DELAY_S:
                return "Akku leer (%.2f V)" % self.avg
        else:
            self.low_since = None
        return None


def read_vbat(bus):
    # Single-Shot, AIN0 gegen GND, PGA +-4,096 V, 128 SPS
    bus.write_i2c_block_data(ADS_ADDR, 0x01, [0xC3, 0x83])
    time.sleep(0.01)
    hi, lo = bus.read_i2c_block_data(ADS_ADDR, 0x00, 2)
    return raw_to_vbat((hi << 8) | lo)


def write_state(avg):
    with open(OUT + ".tmp", "w") as f:
        f.write("%.2f %d\n" % (avg, percent(avg)))
    os.replace(OUT + ".tmp", OUT)


def shutdown(reason):
    subprocess.call(["wall", "GameboyPi: %s - fahre herunter" % reason])
    time.sleep(3)
    subprocess.call(["systemctl", "poweroff"])


def main():
    import RPi.GPIO as GPIO
    import smbus

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LBO_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_OFF)   # R10 zieht hoch
    bus = smbus.SMBus(1)
    mon = Monitor()
    while True:
        try:
            v = read_vbat(bus)
        except OSError:
            v = None
        reason = mon.step(v, GPIO.input(LBO_GPIO) == 0, time.time())
        if mon.avg is not None:
            write_state(mon.avg)
        if reason:
            shutdown(reason)
            return
        time.sleep(INTERVAL_S)


if __name__ == "__main__":
    main()
