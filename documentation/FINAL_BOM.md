# Endgültige Stückliste v1.2

Maschinenlesbar: `bom/bill-of-materials.csv` (alle Positionen) und `bestellung/2_bauteile/digikey_mouser_bom.csv` (Upload für DigiKey/Mouser). Preise und Lieferstatus: [PURCHASING_COMPARISON.md](PURCHASING_COMPARISON.md).
Legende Preisstatus: **geprüft** = Händlerseite am 11.11.2026 abgerufen · *v1.1* = Schätzung aus Okt. 2026, nicht neu geprüft.

## Module

| Ref | Bauteil | Hersteller / Typ | Menge | Kerndaten | Datenblatt | € | Status |
|---|---|---|---|---|---|---|---|
| J1 | Raspberry Pi Zero 2 WH | Raspberry Pi SC0721 | 1 | 4 × A53 1 GHz, 512 MB, WLAN | datasheets.raspberrypi.com/rpizero2 | 22,10 | geprüft (Reichelt) |
| J2 | Display 2,4" ILI9341 SPI mit Touch | LAFVIN (≈ MSP2402) | 1 | 320×240, 77,18 × 42,72 mm, VCC 3,3–5 V | lcdwiki.com MSP2402 | 16,00 | *v1.1* |
| J10 | PowerBoost 1000C | Adafruit 2465 | 1 | 5,2 V, 1 A, Laden 1 A, EN/LBO | learn.adafruit.com/adafruit-powerboost-1000c… | 23,90–25,16 | geprüft |
| J3 | Mono-Verstärker PAM8302 | Adafruit 2130 | 1 | 24 dB, 1,5 W @ 8 Ω, Trimmpoti | diodes.com PAM8302A | 3,90–5,50 | geprüft |
| J11/J12 | 16-Bit-ADC ADS1115 **STEMMA QT** | Adafruit 1085 | 1 | I2C 0x48, Eingang 6 MΩ | ti.com/lit/ds/symlink/ads1115.pdf | 15,90 | geprüft |
| BT1 | LiPo 103450 mit Schutzschaltung, JST-PH 2,0 | diverse | 1 | 3,7 V, ≥ 2000 mAh, ≤ 52 × 34 × 10 mm | – | ≈ 6,50 | *v1.1* |
| LS1 | Lautsprecher 20 mm | PUI Audio AS02008MR-5-R | 1 | 8 Ω, **0,5 W** (max. 0,8 W), 4,2 mm hoch | puiaudio.com specs-AS02008MR-5-R.pdf | ≈ 3,00 | Daten geprüft, Preis *v1.1* |
| – | microSD 32 GB A1 | z. B. Verbatim Premium | 1 | | – | 7–12 | *v1.1* |

## Bauteile auf der Trägerplatine

| Ref | Wert / Typ | Hersteller-Nr. | Menge | Begründung |
|---|---|---|---|---|
| SW1–SW8 | Taster 6 × 6 × 5,0 mm | Omron B3F-1020 | 8 (+2) | Höhe 5,0 mm laut Omron, passt zur Stößellänge |
| SW9 | Schiebeschalter SPDT abgewinkelt | C&K OS102011MA1QN1 | 1 | Hebel durch die Oberkante |
| J7 | Klinke 3,5 mm mit Schaltkontakten | Same Sky SJ1-3525N | 1 | trennt Lautsprecher beim Einstecken |
| RV1 | Poti 10 kΩ log, liegend | Bourns PTV09A-2020F-A103 | 1 | Achse seitlich, abgeflacht |
| Q1, Q2 | N-MOSFET | onsemi BS170 | 2 (+1) | V_GS(th) ≤ 3,0 V bei 1 mA, reicht für 21 µA EN-Strom |
| D2 | Schottky | Vishay BAT85 | 1 (+1) | trennt LBO (bis 4,2 V) vom 3,3-V-GPIO |
| D1 | LED rot 3 mm | Lite-On LTL-4221N | 1 | 3,2 mA über R1 |
| R1 | 1 kΩ | Yageo MFR-25FBF52-1K | 1 | LED-Vorwiderstand |
| R2, R4 | 270 Ω | MFR-25FBF52-270R | 2 | PWM-Filter |
| R3, R5 | 150 Ω | MFR-25FBF52-150R | 2 | PWM-Filter |
| **R6, R7** | **47 kΩ 5 %** (v1.2, vorher 10 kΩ) | Stackpole CF14JT47K0 (DigiKey CF14JT47K0CT-ND) | 2 (10 bestellt) | Lautsprecher ≤ 0,5 W (mit −5 % im ungünstigsten Fall 0,52 W, unter 0,8 W max.). Yageo MFR-25FBF52-47K wäre erst ab 17.03.2027 lieferbar |
| R8 | 1 MΩ | MFR-25FBF52-1M | 1 | Gate-Pull-up Q1 |
| R9, **R10**, R11, R12 | 100 kΩ (R10 v1.2, vorher 10 kΩ) | MFR-25FBF52-100K | 4 | Pull-down, LBO-Pull-up, Spannungsteiler |
| C2, C4 | 33 nF X7R RM 2,5 | Vishay K333K15X7RF5TL2 | 2 | PWM-Filter |
| C6 | 100 nF X7R RM 2,5 | Vishay K104K15X7RF5TL2 | 1 | ADC-Eingang |
| C3, C5 | 100 µF 10 V, Ø 6,3 × 6 mm | Panasonic ECE-A1AKS101 | 2 | Kopfhörer-Koppelkondensator, niedrig |
| C1 | 470 µF 10 V, Ø 6,3 × 11 mm | Rubycon 10YXJ470M6.3X11 | 1 | Puffer +5V |
| J1 | Buchsenleiste 2 × 20, 8,5 mm | Sullins PPTC202LFBN-RC | 1 | Pi kopfüber |
| J8 | Stiftleiste 1 × 3 | Sullins PRPC003SAAN-RC | 1 | UART |
| PCB | Leiterplatte v1.2 | JLCPCB, 2 Lagen, 1,6 mm, HASL | 5 | Mindestmenge |

## Mechanik und Kleinmaterial

M2,5 × 11 Abstandsbolzen (Pi), 4 × M2,5 × 20 Gehäuseschrauben, 2 × M3 × 14 + Mutter (Display), 2 gedruckte 4-mm-Hülsen (`spacers.stl`), PLA schwarz ≈ 70 g + Silk silber/lila je ≈ 5 g, Kapton, Moosgummi 0,5 mm, Litze 0,14 mm², optional Acrylscheibe 62 × 46 × 1 mm.

## Alternativen

| Bauteil | Alternative | Bewertung |
|---|---|---|
| Pi Zero 2 W | Pi Zero W (gleiche Pinbelegung) | passt ohne Änderung, nur GB/GBC/NES flüssig |
| PowerBoost 1000C | TP4056 + MT3608 | abgelehnt: kein Load-Sharing, kein EN/LBO, Poti-Boost kann 12 V liefern |
| ADS1115 Adafruit | China-Klon (blau, 10-polig) | passt **nicht** (andere Pinfolge) |
| PAM8302 Adafruit | PAM8403-Modul | abgelehnt: anderes Pinout, Stereo unnötig |
| Lautsprecher 0,5 W | 20 mm, 1 W, 8 Ω, ≤ 4,5 mm hoch | würde mehr Lautstärke erlauben, R6/R7 dann 33 kΩ |
