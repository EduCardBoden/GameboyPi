# Verdrahtung und Signalfluss

Fast alles läuft über die Trägerplatine. Lose Kabel gibt es nur zwei: den **Akku** (JST-PH, steckt direkt im PowerBoost) und den **Lautsprecher** (zum PAM8302, Kabel durch Loch H5).

## Architektur

```
                 Micro-USB 5V (Laden)
                        │
 LiPo 1S 2000 mAh ──JST──► PowerBoost 1000C ──5,2 V──► +5V ──► Pi Zero 2 W (Pin 2/4)
  (mit Schutz-PCM)        │  BAT ─► R11/R12 ─► ADS1115 AIN0   ├─► Display VCC
                          │  LBO ─► BAT85 ─► GPIO20            ├─► PAM8302 VIN
                          │  EN ◄── Q1 (BS170)                 └─► Power-LED, C1 470 µF
                          │          ▲ Gate: PWR_REQ (R8 1 MΩ nach BAT)
                          │          ├── SW9 Stellung EIN  → GND  (Gerät an)
                          │          └── Q2 (BS170) ◄── GPIO4 „PWR_KEEP“ (gpio-poweroff)
                          │  SW9 Stellung AUS → GPIO16 „PWR_SW_SENSE“ (gpio-shutdown)

 Pi +3V3 ──► Display LED (Hintergrundlicht), ADS1115 VCC, R10 (LBO-Pull-up)
```

### Abschaltlogik

| Zustand | SW9 | GPIO4 | PWR_REQ | Q1 | PowerBoost EN | Ergebnis |
|---|---|---|---|---|---|---|
| aus | AUS | – (Pi aus) | high (R8) | leitet | low | Boost aus, nur ~4 µA Ruhestrom (R8) + 21 µA (Spannungsteiler) |
| einschalten | EIN | – | low (SW9) | sperrt | high | Pi bootet |
| Betrieb | EIN | high | low | sperrt | high | an |
| Schalter auf AUS | AUS | high | low (Q2) | sperrt | high | GPIO16 low → Linux fährt herunter |
| heruntergefahren | AUS | low | high | leitet | low | Strom aus |

Ruhestrom im ausgeschalteten Zustand: ca. 25 µA. Ein 2000-mAh-Akku hält damit rechnerisch Jahre, Selbstentladung und PowerBoost-Ruhestrom kommen noch dazu.

## GPIO-Belegung (Raspberry Pi Zero, 40-polige Leiste)

| Pin | GPIO | Signal | Funktion |
|---|---|---|---|
| 1, 17 | – | +3V3 | Display-Hintergrundlicht, ADS1115, R10 |
| 2, 4 | – | +5V | Versorgung vom PowerBoost |
| 3 | 2 | I2C_SDA | ADS1115 |
| 5 | 3 | I2C_SCL | ADS1115 |
| 7 | 4 | PWR_KEEP | gpio-poweroff (high = an lassen) |
| 8 | 14 | UART_TX | Debug J8 |
| 10 | 15 | UART_RX | Debug J8 |
| 11 | 17 | BTN_START | |
| 13 | 27 | BTN_SELECT | |
| 15 | 22 | BTN_B | |
| 16 | 23 | BTN_A | |
| 18 | 24 | LCD_RST | |
| 19 | 10 | LCD_MOSI | SPI0 |
| 21 | 9 | LCD_MISO | SPI0 (vom Treiber nicht genutzt) |
| 22 | 25 | LCD_DC | |
| 23 | 11 | LCD_SCK | SPI0 |
| 24 | 8 | LCD_CS | SPI0 CE0 |
| 29 | 5 | BTN_UP | |
| 31 | 6 | BTN_DOWN | |
| 32 | 12 | AUD_PWM_L | PWM0 (audremap) |
| 33 | 13 | AUD_PWM_R | PWM1 (audremap) |
| 35 | 19 | BTN_LEFT | |
| 36 | 16 | PWR_SW_SENSE | gpio-shutdown (low = ausschalten) |
| 37 | 26 | BTN_RIGHT | |
| 38 | 20 | LBO_N | Akku < 3,2 V (low) |
| 6, 9, 14, 20, 25, 30, 34, 39 | – | GND | |

Frei: GPIO 7, 18, 21 (Pins 26, 12, 40). GPIO 0/1 (ID-EEPROM) sind bewusst unbenutzt.
Konfliktprüfung: SPI0, I2C1, UART0, PWM0/1 und die Tasten belegen disjunkte Pins. Audio (GPIO12/13) und SPI (GPIO8–11) teilen sich keine Peripherie.

## Modul-Anschlüsse (laut Original-CAD-Daten)

| Modul | Stecker | Pins (1 → n) | Quelle |
|---|---|---|---|
| Display MSP2402 | J2 1×14 | VCC, GND, CS, RESET, DC, SDI, SCK, LED, SDO, T_CLK, T_CS, T_DIN, T_DO, T_IRQ | lcdwiki Benutzerhandbuch + Maßzeichnung |
| PowerBoost 1000C | J10 1×8 | USB, BAT, VS, EN, GND, LBO, GND, 5V | Adafruit Eagle-Datei (Rev B) |
| PAM8302 | J3 1×5 | GND, VIN, SD, A−, A+ | Adafruit Eagle-Datei |
| ADS1115 STEMMA QT | J11 1×6 | VCC, GND, SCL, SDA, ADDR, ALERT | Adafruit Eagle-Datei |
| | J12 1×6 | AVDD, AIN3, AIN2, AIN1, AIN0, AGND | Adafruit Eagle-Datei |
| UART | J8 1×3 | GND, TX, RX | |

## Audiopfad

```
GPIO12 ─270Ω─┬─150Ω─GND          GPIO13 analog ─► AUD_R_F ─► C5 ─► HP_R
             └─33nF─GND
          AUD_L_F ─(+)C3 100µF─► HP_L ─► Klinke T ──(Schaltkontakt TN)──► SPK_L ─10k─┐
                                                                                    ├─ SPK_MIX ─► RV1 10k log ─► AMP_IN ─► PAM8302 A+ (A− = GND) ─► Lautsprecher
                                         HP_R ─► Klinke R ──(Schaltkontakt RN)──► SPK_R ─10k─┘
```
Ohne Stecker verbinden die Schaltkontakte TN/RN Spitze und Ring mit dem Lautsprecherpfad. Mit eingestecktem Kopfhörer sind sie offen, der Lautsprecher ist stumm.
