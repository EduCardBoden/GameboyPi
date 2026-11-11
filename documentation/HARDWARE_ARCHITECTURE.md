# Hardware-Architektur (v1.2)

GPIO-Tabelle, Modul-Pinouts und Abschalt-Wahrheitstabelle: [wiring.md](wiring.md). Hier stehen die Versorgung, die Pegel und die Grenzwerte.

## Blöcke

```
USB 5 V ─► PowerBoost 1000C (MCP73871 Lader 1 A + TPS61090 Boost 5,2 V)
LiPo 3,0–4,2 V ─┘   │ EN ◄─ Q1 BS170 ◄─ PWR_REQ (R8 1 MΩ → VBAT; SW9 / Q2 ziehen auf GND)
                    │ LBO ─► D2 BAT85 ─► GPIO20 (R10 100 kΩ → 3V3)
                    └─► +5V ─► Pi Zero 2 W, Display VCC, PAM8302, LED, C1 470 µF
Pi 3V3 ─► Display-Hintergrundlicht, ADS1115, R10
VBAT ─► R11/R12 100k/100k ─► ADS1115 AIN0 (I2C 0x48)
GPIO12/13 PWM ─► 270 Ω/150 Ω/33 nF ─► C3/C5 100 µF ─► Klinke ─(Schaltkontakt)─► 47k/47k ─► RV1 ─► PAM8302 ─► 8 Ω
```

## Spannungen und Pegel

| Netz | Wert | Quelle / Nachweis |
|---|---|---|
| VBAT | 3,0–4,2 V | LiPo 1S, Schutzschaltung im Akku |
| +5V | 5,2 V (≥ 5,0 V bei > 500 mA) | Adafruit PowerBoost-Anleitung |
| +3V3 | 3,3 V | Regler auf dem Pi |
| Logik Pi ↔ Display, ADS1115 | 3,3 V | Display-Logik 3,3 V (lcdwiki), ADS1115 an 3V3 |
| LBO (PowerBoost) | Open-Drain, Pull-up auf VBAT | TI TPS61090: max. 100 µA Low-Strom |
| EN (PowerBoost) | Pull-up R13 = 200 kΩ an VBAT; aus bei < 0,2 × VBAT | Adafruit Eagle-Schaltplan Rev B, TI-Datenblatt |
| AIN0 | max. 2,1 V (4,2 V / 2) < VDD 3,3 V | ADS1115-Grenze VDD + 0,3 V ✔ |

## Strombudget (am 5-V-Ausgang)

| Verbraucher | typ. | Spitze |
|---|---|---|
| Pi Zero 2 W (Emulation, WLAN an) | 350 mA | 600 mA |
| Display (0,57 W laut Datenblatt) | 115 mA | 115 mA |
| PAM8302 + Lautsprecher (v1.2: max. 0,5 W) | 60 mA | ≈ 120 mA (vorher ≈ 330 mA) |
| Rest (ADS1115, LED 3,2 mA, Pull-ups) | 5 mA | 5 mA |
| **Summe** | **≈ 530 mA** | **≈ 840 mA** (vorher ≈ 1,05 A) |

Die v1.2-Begrenzung der Lautsprecherleistung bringt die Spitzenlast unter die 1-A-Nenngrenze des PowerBoost (README-Risiko 4).

## Abschaltlogik: Nachweis (v1.2)

| Größe | Wert | Folgerung |
|---|---|---|
| EN-Pull-up | 200 kΩ an VBAT (≤ 4,2 V; mit USB an VS ≤ 5,2 V) | Q1 muss ≤ 26 µA ziehen |
| BS170 V_GS(th) | 0,8 / 2,1 / 3,0 V (min/typ/max) bei **I_D = 1 mA** | bei V_GS = VBAT ≥ 3,0 V fließen ≥ 1 mA ≫ 26 µA ✔ |
| EN-Schaltschwelle | V_IL = 0,2 × VBAT (≥ 0,6 V) | Q1 zieht EN auf wenige mV ✔ |
| Q2 | Gate an GPIO4 = 3,3 V, muss 4,2 µA (R8) halten | ✔ |
| Ruhestrom aus | R8 4,2 µA + R11/R12 21 µA ≈ 25 µA | |

Bekannte Bedieneigenschaft: Wird der Schalter während des Herunterfahrens wieder auf EIN gestellt, hält der Schalter die Versorgung, obwohl der Pi angehalten ist. Abhilfe: einmal AUS, dann EIN.
