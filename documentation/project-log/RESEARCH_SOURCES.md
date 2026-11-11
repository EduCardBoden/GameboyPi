# Quellen

Alle Quellen am **11.11.2026** abgerufen. „bestätigt“ = Wert direkt im Dokument gelesen. „Suchergebnis“ = nur der Ausschnitt der Suchmaschine, die Seite selbst wurde nicht geöffnet.

## Datenblätter und Herstellerunterlagen

| Thema | Quelle | Verwendeter Wert | Status |
|---|---|---|---|
| TPS61090 (Boost im PowerBoost) | https://www.ti.com/lit/ds/symlink/tps61090.pdf | LBO Open-Drain, V_OL ≤ 0,4 V bei 100 µA, Low-Strom 100 µA; EN V_IL 0,2 × VBAT, V_IH 0,8 × VBAT | bestätigt (PDF-Text) |
| ADS1115 | https://www.ti.com/lit/ds/symlink/ads1115.pdf | Gleichtakt-Eingangsimpedanz 6 MΩ (±4,096 V), differentiell 15 MΩ | bestätigt (PDF-Text) |
| PowerBoost 1000C Schaltplan Rev B | https://github.com/adafruit/Adafruit-PowerBoost-1000C (`…Rev B.sch`) | R13 = 200 kΩ zwischen VBAT und ENABLE (Netz JP2-4, U1 EN) | bestätigt (Eagle-XML) |
| PowerBoost 1000C Pinbelegung | https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/pinouts | EN gegen GND = aus; LBO < 3,2 V; 5 V sinkt ab 500 mA Richtung 5,0 V | bestätigt |
| PowerBoost EN-Pull-up an VS statt VBAT | https://forums.adafruit.com/viewtopic.php?t=112092 | Abweichung Schaltplan ↔ Platine (R13 an VS) | bestätigt (Forum, Nutzerbeitrag) |
| PAM8302A | https://cdn-shop.adafruit.com/datasheets/PAM8302A.pdf | max. Verstärkung 24 dB, R_i min. 10 kΩ | Suchergebnis (PDF nicht lesbar abgerufen) |
| Adafruit PAM8302 | https://www.adafruit.com/product/2130 | feste 24 dB, Trimmpoti, 1,5 W @ 8 Ω 10 % THD 5,5 V, 1 µF Eingangskondensatoren | bestätigt |
| BS170 | https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf, Mouser-Kopie | V_GS(th) 0,8 / 2,1 / 3,0 V bei V_DS = V_GS, I_D = 1 mA | Suchergebnis + onsemi-Community |
| Omron B3F | https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf | B3F-1020 Höhe 5,0 ± 0,2 mm | Suchergebnis (Omron, Farnell) |
| PUI AS02008MR-5-R | https://puiaudio.com/file/specs-AS02008MR-5-R.pdf | 0,5 W Nenn-, 0,8 W Maximalleistung, 8 Ω ± 15 % | Suchergebnis (PUI, DigiKey) |
| fbcp-ili9341 | https://github.com/juj/fbcp-ili9341 (README) | Teiler 6 typisch für ILI9341, kein `dtparam=spi=on`, `SINGLE_CORE_BOARD` nur Zero/Zero W, 64-Bit nicht unterstützt | bestätigt |
| IPC-2221 | Formel I = k · ΔT^0,44 · A^0,725, k = 0,048 (Außenlage) | Leiterbahntabelle | Standardformel |

## Händler und Lieferlage

| Händler | URL | Status |
|---|---|---|
| BerryBase.at Pi Zero 2 WH | https://www.berrybase.at/raspberry-pi-zero-2-wh | bestätigt (Seite) |
| BerryBase.at Pi Zero 2 W | https://www.berrybase.at/raspberry-pi-zero-2-w | bestätigt |
| BerryBase.at PowerBoost | https://www.berrybase.at/adafruit-powerboost-1000 | bestätigt |
| BerryBase.at PAM8302 | https://www.berrybase.at/adafruit-mono-2.5w-class-d-audio-verstaerker-pam8302 | bestätigt |
| BerryBase.at ADS1115 | https://www.berrybase.at/en/adafruit-ads1115-16-bit-adc-4-channel-with-programmable-amplifier | bestätigt |
| Reichelt Pi Zero 2 WH / W, PowerBoost | reichelt.com …-383360, reichelt.at …-313902, …-235493 | Suchergebnis (Reichelt blockt den Abruf) |
| Kiwi Electronics, Botland, Paradisetronic | jeweilige Produktseite | Suchergebnis |
| Lieferlage Pi Zero 2 W | https://raspberry.tips/raspberrypi-infos/raspberry-pi-zero-2-w-alternative-ausverkauft (geändert 08.11.2026) | bestätigt (Artikel) |
| Adafruit-Listenpreise | adafruit.com/product/1085, /2130, /2465 | Suchergebnis |
