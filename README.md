# GameboyPi v1.1 – Raspberry-Pi-Zero-Handheld im Game-Boy-Color-Stil

Tragbarer Retro-Handheld mit eigener Trägerplatine (KiCad 10), 3D-druckbarem Gehäuse (OpenSCAD) und LiPo-Akku.
**Status: Design fertig und rechnerisch geprüft, aber noch nicht gebaut.** Siehe [Prüfstatus](documentation/testing.md) und [offene Risiken](#offene-technische-risiken).

| | |
|---|---|
| Rechner | Raspberry Pi Zero 2 W (Zero W / Zero kompatibel) |
| Display | 2,4" ILI9341 SPI, 320×240 (MSP2401), 60 fps mit fbcp-ili9341 |
| Bedienung | D-Pad, A, B, Start, Select, Ein/Aus-Schiebeschalter (sicheres Herunterfahren), Lautstärkeknopf |
| Audio | 20-mm-Lautsprecher (PAM8302, 2,5 W) + 3,5-mm-Kopfhörerbuchse mit Lautsprecher-Abschaltung |
| Akku | LiPo 103450, 2000 mAh, PowerBoost 1000C (Micro-USB-Laden, Spielen beim Laden, Lade-LEDs) |
| Laufzeit | ca. 2 h typisch (1,5–2,7 h), [Rechnung](documentation/battery-runtime.md) |
| Gehäuse | 84 × 140 × 28 mm (Original-GBC: 78 × 133,5 × 27,4 mm), Design **„GBX – Game Boy Emulator“**: schwarz mit Fasen, Logo in Chrom-Silber/Lila vorne und hinten ([Vorschau](mechanical/previews/design_front.png), [Rückseite](mechanical/previews/design_back.png)) |
| Kosten | ca. 120 € ([Stückliste](bom/bill-of-materials.csv)) |
| Wartung | microSD seitlich, Mini-HDMI + Micro-USB-Daten oben, UART-Konsole (J8), 6 Testpunkte |

## Projektstruktur

```
GameboyPi/
├── README.md                     ← diese Datei
├── bom/bill-of-materials.csv     ← Stückliste mit Bezugsquellen und Preisen
├── electronics/
│   ├── kicad-project/            ← KiCad-Projekt + Generator-Skripte (design.py = zentrale Netzliste)
│   ├── gerber/                   ← Gerber + Bohrdaten + GameboyPi_Gerber.zip (zum Hersteller)
│   ├── schematics/               ← Schaltplan als PDF
│   └── assembly/                 ← Pick&Place-CSV, KiCad-BOM, Bestückungspläne (PDF), 3D-Renderings, STEP
├── mechanical/
│   ├── cad-source/               ← gameboy_pi_case.scad (parametrisch) + build.ps1 (Kollisionsprüfung, STL)
│   │   ├── logo/                 ← GBX-Logo: Originalbild, trace_logo.py (Vektorisierung), gbx_logo.scad
│   │   └── fonts/                ← Michroma (SIL Open Font License) für die Slogans
│   ├── stl/                      ← front, back, dpad, ab, startselect, knob + 4 Logo-Einlagen (silber/lila)
│   └── previews/                 ← Vorschaubilder
├── software/
│   ├── setup-guide.md            ← RetroPie-Einrichtung, Treiber, Tasten, Audio, Akku, Herunterfahren
│   └── configuration/            ← config.txt-Ergänzung, install.sh, Akku-Dienst
├── documentation/
│   ├── wiring.md                 ← Architektur, GPIO-Belegung, Modul-Pinouts, Abschaltlogik
│   ├── assembly-guide.md         ← Werkzeug, Lötreihenfolge, Druck, Endmontage
│   ├── testing.md                ← durchgeführte Prüfungen + Inbetriebnahme-Messplan
│   └── battery-runtime.md        ← Stromverbrauch, Laufzeit, Lade-/Entladeströme, Kabel
├── tools/freerouting/            ← Autorouter (wird von build.ps1 genutzt)
└── .vscode/                      ← Tasks: Strg+Shift+B baut alles
```

## Bauen (VS Code)

Den Ordner in VS Code öffnen, dann **Strg+Shift+B** („Alles bauen“). Alternativ einzeln über *Terminal → Task ausführen*:

- **Platine bauen (KiCad):** Schaltplan → Platine → Freerouting → ERC/DRC → Gerber, BOM, Pick&Place, PDFs, Renderings (~3 min)
- **Gehäuse bauen (OpenSCAD):** Kollisionsprüfung aller Bauteile gegen die Schalen → STLs → Vorschaubilder
- **Nur STLs exportieren**, **Platine in KiCad öffnen**, **Gehäuse in OpenSCAD öffnen**

Benötigt (installiert): KiCad 10.0, OpenSCAD 2021.01, Java 25 (Microsoft OpenJDK) für Freerouting 2.5.

## Komponenten- und Architekturentscheidungen

| Entscheidung | Begründung |
|---|---|
| **Pi Zero 2 W** kopfüber auf der Platinenrückseite | 4 Kerne (SNES/PS1 flüssig), gleiche Pinbelegung wie Zero/Zero W. Kopfüber wird das Gerät flacher, HDMI/USB zeigen zur Oberkante. |
| **2,4" ILI9341 SPI (MSP2401)** | Passt in die GBC-Breite. Der Linux-Treiber fbcp-ili9341 ist erprobt (DMA, 60 fps, geringe Latenz). Maße stammen aus der Herstellerzeichnung. Ohne Touch, weil dünner. |
| **Adafruit PowerBoost 1000C** statt TP4056 + MT3608 | Geprüftes Modul mit Load-Sharing (laden und spielen), festen 5,2 V (kein Einstell-Poti, das ab Werk 12 V liefern kann), EN-Eingang für die Abschaltlogik, LBO-Signal und Lade-LEDs. |
| **Soft-Power mit 2 × BS170** | Der Schalter trennt nicht hart. Er fordert das Herunterfahren an, und der Pi schaltet sich danach selbst ab. Schützt die SD-Karte. |
| **PWM-Audio + PAM8302 + Klinke mit Schaltkontakt** | Ein Audiopfad für beides: Kopfhörer bekommen Line-Pegel, der Lautsprecher bekommt Verstärker und Lautstärkepoti. Ein I2S-Verstärker (v1.0) kann keine Kopfhörer treiben. |
| **ADS1115** an VBAT/2 | Pi hat keinen ADC. Liefert Akkustand in % plus Abschaltung bei leerem Akku. |
| **Nur THT-Bauteile + Module** | Von Hand lötbar, keine SMD-Bestückung beim Hersteller nötig. |

## Stückliste (Kurzfassung, Details in `bom/bill-of-materials.csv`)

| Teil | ca. € |
|---|---|
| Raspberry Pi Zero 2 W (mit Stiftleiste) + 2×20-Buchse + Abstandsbolzen | 22,50 |
| microSD 32 GB | 7,00 |
| Display MSP2401 + M3-Abstandshalter | 7,80 |
| Adafruit PowerBoost 1000C | 22,00 |
| LiPo 103450 2000 mAh mit Schutz | 10,00 |
| Adafruit PAM8302 + Lautsprecher 20 mm | 7,00 |
| Adafruit ADS1115 | 15,00 |
| Taster, Schalter, Klinke, Poti, MOSFETs, Diode, LED, R/C, Stiftleisten | ≈ 7,20 |
| Leiterplatte (5 Stk. inkl. Versand) | 15,00 |
| Schrauben, Filament, Kleinmaterial, Acrylscheibe | ≈ 6,90 |
| **Summe** | **≈ 120 €** |

## Benötigtes Werkzeug

Temperaturgeregelter Lötkolben + Zinn + Flussmittel, Seitenschneider, Abisolierzange, Pinzette, **Multimeter**, Schraubendreher PH0/PH1, Messschieber, FDM-3D-Drucker. Optional: USB-UART-Adapter (3,3 V), Labornetzteil mit Strombegrenzung. Details in [assembly-guide.md](documentation/assembly-guide.md).

## Montage in Kurzform

1. Platine mit `electronics/gerber/GameboyPi_Gerber.zip` bestellen. Gehäuseteile aus `mechanical/stl/` drucken.
2. Vorderseite bestücken (R, C, LED, Taster, Schalter, Klinke), dann die Rückseite (R, D, Q, C1, Poti, UART, Pi-Buchse, Module).
3. **Inbetriebnahme ohne Pi** nach [testing.md](documentation/testing.md): Testpunkte messen, Abschaltlogik prüfen.
4. Display auf 4-mm-Abstandshalter setzen und verlöten.
5. Tasten, Lautsprecher und Platine in die Vorderschale legen, Akku in den Akkurahmen, Pi aufstecken, Rückschale verschrauben, Knopf aufstecken.
6. Software nach [setup-guide.md](software/setup-guide.md) einrichten.

## Erwartete Akkulaufzeit

≈ **2,1 h** typisch, 2,7 h bei Game Boy/NES mit WLAN aus, 1,5 h unter Dauervolllast. Laden mit 1 A in ≈ 2,5 h, Spielen währenddessen möglich. Rechenweg in [battery-runtime.md](documentation/battery-runtime.md).

## Offene technische Risiken

Ehrliche Liste dessen, was nur rechnerisch geprüft ist oder auf Annahmen beruht. **Vor der Bestellung von 5 Platinen lesen.**

1. **Nicht physisch gebaut oder gemessen.** ERC, DRC, Netzlistenvergleich und die Kollisionsprüfung im CAD sind bestanden. Es gab aber keinen Probedruck, keine Messung und keine Schaltungssimulation (SPICE) der Abschaltlogik.
2. **Soft-Power:** Die Gate-Schwelle des BS170 liegt bei max. 3,0 V. Q1 bekommt sein Gate von VBAT (3,2–4,2 V). Bei fast leerem Akku schaltet Q1 nur knapp durch. Der EN-Eingang braucht laut Adafruit nur einen Pegel nahe GND bei kleinem Strom, das sollte reichen. Wert des internen EN-Pull-ups ist nicht dokumentiert. **Im Messplan prüfen.**
3. **gpio-poweroff:** Das Overlay ist für eine solche Abschaltung gedacht. Das Verhalten hängt aber von der Kernel-Version ab (RetroPie 4.8 / Buster). Falls GPIO4 nach dem Herunterfahren nicht low geht, kann ein systemd-Skript in `/lib/systemd/system-shutdown/` das übernehmen.
4. **PowerBoost-Grenze 1 A:** Die geschätzte Spitzenlast liegt bei ≈ 1 A (Pi-Last + laute Passagen). Mögliche Folge: Spannungseinbrüche unter 5 V, Unterspannungswarnung. Gegenmittel: 8-Ω-Lautsprecher, C1 470 µF, WLAN aus.
5. **Gehäusemaße teils angenommen:** Display, Pi, PowerBoost, PAM8302 und ADS1115 stammen aus Herstellerdaten. **Nicht verifiziert** sind die Bauhöhen von Poti PTV09A-2 (≈ 11,5 mm angenommen), Klinke SJ1-3525N (5,2 mm), Elkos und Lautsprecher, ebenso die genaue Lage der PowerBoost-LEDs unter dem Lichtleiter. Die Öffnungen sind großzügig, trotzdem zuerst die Frontschale probedrucken.
6. **Kollisionsprüfung mit Hüllquadern:** Sie prüft vereinfachte Quader gegen die Schalen, keine exakten 3D-Modelle.
7. **Display-Variante:** Die Werte gelten für das MSP2401. Das MSP2402 (Touch) ist dicker, dann `lcd_spacer`/`lcd_gap` in der `.scad` anpassen. Andere 2,4"-Module (70,5 mm breit) passen nicht.
8. **PWM-Audio:** Leichtes Rauschen ist typisch. Kopfhörerpegel ist Line-Niveau (≈ −12 dB an 32 Ω), also eher leise. Die Kopfhörer-Lautstärke wird nur per Software geregelt, der Knopf regelt nur den Lautsprecher.
9. **Autorouting:** Freerouting hat geroutet. Engstellen gibt es zwischen den Pi-Pins mit 0,15 mm (fertigbar ab 0,127 mm). Ein menschlicher Review des Layouts (z. B. PWM-Audio neben SPI-Takt) ist empfehlenswert.
10. **Wärme:** Der Pi Zero 2 W im geschlossenen Gehäuse kann bei Dauerlast drosseln. Lüftungsschlitze sind vorhanden, eine thermische Simulation fehlt.
11. **Akkuanzeige im Bild** ist nicht umgesetzt (nur `/dev/shm/battery` + automatische Abschaltung). Ein Overlay (z. B. pngview) wäre der nächste Schritt.
12. **Software-Stack:** RetroPie 4.8 basiert auf Debian Buster (nicht mehr gepflegt). fbcp-ili9341 braucht diesen Legacy-Grafikstack. Die Bookworm-Alternative (mipi-dbi-spi) ist dokumentiert, aber langsamer.
13. **Akku-Steckerpolarität:** JST-PH-Akkus gibt es mit vertauschter Belegung. Vor dem Einstecken messen.
14. **Bestückungsdruck:** ca. 100 kosmetische Warnungen (Text auf Pads/Kante). Der Hersteller beschneidet sie, keine Funktion betroffen.

## Rechtliches

Nur eigene, rechtmäßig erworbene Spiele und BIOS-Dateien verwenden. Das Gehäuse ist vom Game Boy Color *inspiriert* und trägt das eigene „GBX“-Logo. Der Slogan „GAME BOY EMULATOR“ enthält die Marke „Game Boy“ (Nintendo). Für ein privates Einzelstück ist das unproblematisch. Wer Gehäuse oder Geräte verkaufen will, sollte den Slogan in `gameboy_pi_case.scad` (`back_silver_2d`) ändern.
