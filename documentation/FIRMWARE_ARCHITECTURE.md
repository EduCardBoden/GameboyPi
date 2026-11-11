# Software-Architektur (v1.2)

Das Gerät hat **keinen Mikrocontroller und keine AVR/Arduino-Firmware**. Die gesamte Logik läuft unter Linux auf dem Pi Zero 2 W (RetroPie 4.8, Debian Buster, 32 Bit). „Firmware“ heißt hier: Device-Tree-Overlays, der Display-Treiber und ein Python-Dienst. Einrichtung: [../software/setup-guide.md](../software/setup-guide.md).

## Bausteine

| Baustein | Datei | Aufgabe |
|---|---|---|
| Boot-Konfiguration | `software/configuration/config.txt.append` | HDMI 320×240 als Quelle für fbcp, PWM-Audio (audremap 12/13), I2C, UART, 8 × `gpio-key`, `gpio-shutdown`, `gpio-poweroff`, GPIO20 ohne Pull |
| Display-Treiber | fbcp-ili9341 (GitHub juj), gebaut von `install.sh` | Kopiert den Framebuffer per SPI0 + DMA aufs ILI9341, nur geänderte Bereiche, Taktteiler 6 |
| Akku-Dienst | `battery_monitor.py` + `gameboypi-battery.service` | ADS1115 alle 5 s lesen, `/dev/shm/battery` schreiben, bei leerem Akku herunterfahren |
| Installation | `install.sh` | idempotent, Root-Prüfung, Sicherung von `/boot/config.txt` |
| Tests | `software/tests/test_battery_monitor.py` | 7 Unit-Tests ohne Hardware |

## Schnittstellen und Takt

| Schnittstelle | Pins (BCM) | Takt / Parameter |
|---|---|---|
| SPI0 Display | SCLK 11, MOSI 10, MISO 9, CE0 8, DC 25, RST 24 | core_freq / 6 (fbcp-Empfehlung für ILI9341). Bei Bildfehlern 8 oder 10 |
| I2C1 ADS1115 | SDA 2, SCL 3 | 100 kHz Standard, Adresse 0x48 (ADDR = GND) |
| PWM-Audio | 12 (L), 13 (R) | PWM0/1, RC-Tiefpass 270/150 Ω, 33 nF → f_g ≈ 50 kHz |
| Tasten | 5, 6, 19, 26, 23, 22, 17, 27 | `gpio-key` (Kernel entprellt), interne Pull-ups, aktiv low |
| Ein/Aus | 16 (Schalter), 4 (Halten) | `gpio-shutdown` (low = herunterfahren), `gpio-poweroff` (active_low: high im Betrieb, low nach Halt) |
| LBO | 20 | Eingang ohne Pull, R10 100 kΩ extern |
| UART | 14/15 | 115200 Baud Konsole |

Die Belegung prüft `tools/check_consistency.py` automatisch gegen `PI_PINS` in `design.py`.

## Akku-Dienst: Ablauf

```
alle 5 s: U = Rohwert · 4,096/32768 · 2,0167 · VBAT_CAL
          avg = 0,8 · avg + 0,2 · U          (gleitender Mittelwert)
          /dev/shm/battery ← "3.86 68"
          LBO low 3× in Folge (15 s)        → herunterfahren
          avg < 3,30 V länger als 30 s       → herunterfahren
          ADS1115 nicht erreichbar           → nur LBO überwachen
```

Die Entscheidungslogik steckt in der Klasse `Monitor` ohne Hardwarezugriff, darum ist sie auf jedem PC testbar.

## Änderungen v1.2

| Änderung | Grund |
|---|---|
| Teilerfaktor 2,0167 statt 2,0 | ADS1115-Eingangsimpedanz 6 MΩ belastet R12 (−0,8 %) |
| `VBAT_CAL` | einmaliger Abgleich mit Multimeter an TP1 |
| LBO entprellt (3 Messungen) | kurze Lastspitzen lösten sonst sofort eine Abschaltung aus |
| `PUD_OFF` + `gpio=20=ip,pn` | LBO-Strom unter 100 µA (TPS61090-Spezifikation) |
| Hardware-Imports in `main()` | Tests ohne Pi möglich |
| `install.sh`: `set -euo pipefail`, Root-Prüfung, Wiederanlauf nach abgebrochenem Clone, Upgrade-Pfad v1.1 → v1.2 | Robustheit |

## Leistung und Speicher

- fbcp-ili9341 braucht laut Projekt mit DMA wenige % CPU eines Kerns. Der Zero 2 W hat 4 Kerne, also bleibt genug für die Emulation.
- `battery_monitor.py`: ein I2C-Zugriff alle 5 s, vernachlässigbare CPU-Last, ≈ 10 MB RAM (Python).
- 512 MB RAM: GPU-Speicher auf RetroPie-Standard lassen. fbcp braucht keinen zusätzlichen.

## Bekannte Grenzen

- fbcp-ili9341 braucht den Legacy-Grafikstack (Buster, 32 Bit). Auf 64-Bit- oder Bookworm-Systemen läuft er nicht (README-Risiko 12).
- `gpio-poweroff` ist auf echter Hardware nicht getestet (README-Risiko 3).
- Keine Akkuanzeige im Bild (Roadmap).
