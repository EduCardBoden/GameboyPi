# Software-Einrichtung

## Auswahl

| Option | Bewertung für dieses Gerät |
|---|---|
| **RetroPie 4.8** (Image „Pi 2/3/Zero 2 W“, Basis Raspberry Pi OS Buster) | **gewählt.** Läuft auf Zero 2 W und Zero W, große Emulator-Auswahl, EmulationStation startet automatisch. Buster nutzt noch den Legacy-Grafikstack, den `fbcp-ili9341` braucht. |
| Recalbox | Komfortabel, aber eigenes Read-only-System. Eigene Overlays und Treiber wie `fbcp-ili9341` sind schwer einzubinden. |
| Raspberry Pi OS Bookworm + RetroArch | Aktuellster Kernel. Das SPI-Display liefe über den DRM-Treiber `mipi-dbi-spi` (braucht eine eigene ILI9341-Init-Datei) und ist deutlich langsamer als `fbcp-ili9341`. Nur zu empfehlen, wenn ein aktuelles OS Pflicht ist. |

Pi-Varianten: **Zero 2 W** (empfohlen, bis PlayStation 1 / SNES flüssig), **Zero W / Zero** (GB, GBC, NES, Master System, einfache SNES-Spiele). Auf dem Zero/Zero W das RetroPie-Image „Pi 0/1“ verwenden. Pinbelegung und Hardware sind identisch.

## Installation

1. RetroPie 4.8 mit dem Raspberry Pi Imager auf die microSD schreiben (Zero 2 W: Image für Pi 2/3).
2. Für die Ersteinrichtung HDMI-Monitor und USB-Tastatur über ein OTG-Adapterkabel am Micro-USB-Datenport anschließen. Der Port ist durch die Öffnung in der Oberkante erreichbar.
3. In RetroPie: `sudo raspi-config` → WLAN, Locale, SSH aktivieren. Unter „Interface“ **nicht** SPI aktivieren.
4. Den Ordner `software/configuration/` auf den Pi kopieren (z. B. per `scp`) und ausführen:
   ```bash
   sudo bash install.sh
   sudo reboot
   ```
   Das Skript ergänzt `/boot/config.txt` (mit Sicherungskopie), baut `fbcp-ili9341` und richtet zwei Dienste ein: `fbcp-ili9341` für das Display und `gameboypi-battery` für die Akkuüberwachung.
5. Nach dem Neustart erscheint EmulationStation auf dem 2,4"-Display. Dort **Configure Input** wählen und die Tasten anlernen (sie melden sich als Tastatur).
6. Spiele (nur eigene, rechtmäßig erworbene ROM-Kopien und BIOS-Dateien) nach `~/RetroPie/roms/<system>/` kopieren, per WLAN (Samba-Freigabe `\\retropie`) oder USB-Stick.

## Display

- Treiber: [fbcp-ili9341](https://github.com/juj/fbcp-ili9341). Er kopiert den HDMI-Framebuffer (320×240, per `hdmi_cvt` erzwungen) per DMA auf das ILI9341, mit bis zu 60 fps bei kleiner Latenz.
- Pins: SPI0 MOSI/SCK/CE0 (GPIO 10/11/8), DC = GPIO25, RST = GPIO24. Die Hintergrundbeleuchtung hängt fest an 3,3 V.
- Steht das Bild falsch herum, an die `cmake`-Zeile in `install.sh` `-DDISPLAY_ROTATE_180_DEGREES=ON` anhängen. Bei vertauschten Farben `-DDISPLAY_SWAP_BGR=ON`.

## Tasten

| Taste | GPIO | Keycode | Taste in Linux |
|---|---|---|---|
| UP | 5 | 103 | Pfeil hoch |
| DOWN | 6 | 108 | Pfeil runter |
| LEFT | 19 | 105 | Pfeil links |
| RIGHT | 26 | 106 | Pfeil rechts |
| A | 23 | 45 | X |
| B | 22 | 44 | Z |
| START | 17 | 28 | Enter |
| SELECT | 27 | 54 | Shift rechts |

Hotkey (RetroArch, Standard bei Tastatur-Konfiguration): **SELECT + START** beendet das Spiel.

## Audio und Lautstärke

- PWM-Stereo über `dtoverlay=audremap,pins_12_13` (GPIO12 = links, GPIO13 = rechts).
- **Lautsprecher:** Hardware-Lautstärke über den Drehknopf links (Poti RV1 vor dem PAM8302). Seit v1.2 begrenzen R6/R7 (47 kΩ) die Leistung auf ≤ 0,5 W, damit der 0,5-W-Lautsprecher bei Vollausschlag nicht überlastet wird. Das Trimmpoti auf dem PAM8302-Modul bleibt auf Rechtsanschlag (Werkseinstellung) und dient nur zur Feinabstimmung nach unten.
- **Kopfhörer:** Beim Einstecken trennt die Buchse den Lautsprecher automatisch. Die Kopfhörer-Lautstärke lässt sich in EmulationStation unter *Sound Settings → System Volume* einstellen, oder mit `amixer set PCM 80%`.
- Ausgabegerät in RetroPie auf „Headphones/Analog“ stellen: `sudo raspi-config` → System → Audio.

## Akku

- Die Lade-LEDs des PowerBoost (gelb = lädt, grün = voll) sind durch das Fenster „CHG“ auf der Rückseite sichtbar.
- Der Dienst `gameboypi-battery` schreibt Spannung und Prozent nach `/dev/shm/battery` (z. B. `3.86 68`).
- Bei Akku < 3,2 V (PowerBoost-Ausgang LBO auf GPIO20, 3 Messungen in Folge = 15 s) oder 30 s unter 3,30 V fährt das Gerät automatisch herunter.
- **Abgleich der Spannungsanzeige (einmalig):** Spannung an TP1 mit dem Multimeter messen, mit `cat /dev/shm/battery` vergleichen und in `/opt/gameboypi/battery_monitor.py` `VBAT_CAL = Multimeter / Anzeige` setzen (z. B. 3,912 / 3,897 = 1.004), dann `sudo systemctl restart gameboypi-battery`. Die Software rechnet die 6-MΩ-Eingangsimpedanz des ADS1115 bereits heraus.
- **Tests ohne Pi:** `python -m pytest software/tests -q` (Repo-Wurzel) prüft die Rechenlogik.
- Eine Akkuanzeige *im Bild* ist nicht enthalten. Ein mögliches Overlay wäre `pngview` aus raspidmx mit Werten aus `/dev/shm/battery` (siehe offene Punkte in der README).

## Sicheres Herunterfahren

1. Den Schalter auf AUS stellen: GPIO16 geht auf low, `gpio-shutdown` startet `systemctl poweroff`.
2. Nach dem Herunterfahren schaltet `gpio-poweroff` GPIO4 auf low. Dadurch sperrt Q2, R8 zieht PWR_REQ hoch, Q1 zieht den EN-Eingang des PowerBoost auf GND, und der Strom ist aus.
3. Bis dahin bleibt die Versorgung erhalten, die SD-Karte wird nicht beschädigt.

Hinweis: Wird der Schalter während des Herunterfahrens wieder auf EIN gestellt, bleibt der Pi im angehaltenen Zustand. Dann einmal AUS und wieder EIN schalten.

## Automatischer Start

RetroPie startet nach dem Booten automatisch in EmulationStation (Autologin auf Konsole, `raspi-config` → System → Boot/Auto Login). `fbcp-ili9341` läuft als Dienst ab `sysinit.target`, sodass schon der Bootvorgang auf dem Display sichtbar ist.

## Debug / Wartung

- **UART-Konsole** an J8 (GND / TX / RX, 3,3-V-Pegel, 115200 Baud), z. B. mit einem USB-UART-Adapter. Damit hast du ein Login, auch wenn Display oder WLAN nicht laufen.
- **SSH** über WLAN, **microSD** von der rechten Seite zugänglich, **Micro-USB-Datenport** und **Mini-HDMI** oben.
