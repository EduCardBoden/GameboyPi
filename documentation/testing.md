# Prüfungen und Inbetriebnahme

## A) Durchgeführte Prüfungen (rechnerisch, am 2026-10-20)

Alle Prüfungen laufen automatisch über `electronics/kicad-project/build.ps1` und `mechanical/cad-source/build.ps1`. Die Rohberichte liegen in `electronics/kicad-project/build/` bzw. `mechanical/cad-source/build/`.

| Prüfung | Werkzeug | Ergebnis |
|---|---|---|
| Netzliste Schaltplan ↔ `design.py` (jede Pin-Netz-Zuordnung) | `check_netlist.py` (kicad-cli Netzlistenexport) | **0 fehlend, 0 zusätzlich** |
| Elektrische Regeln (ERC), alle Schweregrade | `kicad-cli sch erc --severity-all` | **0 Fehler, 0 Warnungen** |
| Schaltplan ↔ Platine (Parität) | `kicad-cli pcb drc --schematic-parity` | **0 Abweichungen** |
| Ungeroutete Verbindungen | DRC | **0** |
| Design-Regeln (DRC): Abstände, Bohrungen, Randabstand 0,5 mm (Leiterbahnen ≥ 1 mm), Leiterbahnbreite ≥ 0,15 mm | `kicad-cli pcb drc --severity-all` | **0 Fehler**, 105 Warnungen (siehe unten) |
| Fertigbarkeit | Regeln: min. Bahn 0,15 mm, min. Abstand 0,2 mm, Via 0,6/0,3 mm, Bohrung ≥ 0,7 mm | innerhalb der Standardregeln von JLCPCB/PCBWay (0,127 mm / 0,127 mm / 0,45/0,2 mm) |
| Bauteilorientierung | Abgleich der Pad-1-Positionen mit den Original-CAD-Daten der Module (Adafruit Eagle-Dateien, lcdwiki-Maßzeichnung), Ausgabe von `make_pcb.py` | PowerBoost Pin 1 (USB) unten, PAM8302 Pin 1 (GND) links, ADS1115 Pin 1 unten, Display Pin 1 (VCC) oben, Pi Pin 1 rechts (Rückseite gespiegelt) – wie vorgesehen |
| Mechanik: Kollision Bauteile ↔ Gehäuse | OpenSCAD, 21 Hüllkörper (Platine, Display, Pi, Akku, Module, Taster, Klinke, Poti, Elkos, Lautsprecher) gegen beide Schalen | **0 Kollisionen** (`mechanical/cad-source/build/collision_report.txt`). Im ersten Lauf gefunden und behoben: Pi-Ecke nur 0,16 mm vom Schraubpfosten → Pfosten auf Ø5,5 verkleinert (0,41 mm) |
| STL-Geometrie | OpenSCAD/CGAL | alle 10 Teile exportiert. Schalen, D-Pad und Knopf sind je ein geschlossener Körper, A/B und Start/Select je 2. Logo-Einlagen bestehen aus mehreren Buchstaben-Körpern. |
| Logo-Lesbarkeit | Renderings `previews/design_front.png`, `design_back.png` | Vorderseite von vorne, Rückseite von hinten lesbar (nicht gespiegelt). Einlagen liegen deckungsgleich in den 0,6-mm-Vertiefungen. |

### Verbleibende DRC-Warnungen (bewusst akzeptiert)

| Anzahl | Art | Begründung |
|---|---|---|
| 65 | `silk_overlap` | Referenztexte überlappen sich (dicht bestückte Bereiche). Nur kosmetisch. |
| 29 | `silk_over_copper` | Bestückungsdruck reicht an Pads heran. Der Hersteller entfernt Druck auf Pads automatisch. |
| 8 | `silk_edge_clearance` | Bauteilumrisse von Schalter, Klinke und Poti ragen absichtlich über den Platinenrand. |
| 3 | `starved_thermal` | GND-Pads mit nur einem Thermal-Steg. Diese Pads sind zusätzlich über geroutete GND-Leiterbahnen angebunden. |

Bewusst deaktivierte Regeln (in `GameboyPi.kicad_pro` mit Begründung in `make_pcb.py`):
- `pth_inside_courtyard` / `npth_inside_courtyard`: Lötpins des Schalters und die Mutter des Display-Abstandshalters liegen unter dem Pi, der 11 mm höher sitzt.
- `lib_footprint_mismatch`: Aus dem Klinken-Footprint wurden die Platinenkontur-Linien entfernt. Sie hätten die Platinenkontur zerstört.

### Was NICHT geprüft werden konnte

- **Kein realer Aufbau, keine Messung, kein Probedruck.** Es gibt keine Hardware.
- **Keine Schaltungssimulation** (SPICE) der Abschaltlogik und des Audio-Filters. Für PowerBoost, PAM8302 und ADS1115 gibt es keine öffentlichen SPICE-Modelle. Die Logik ist im Abschnitt „Abschaltlogik“ in `wiring.md` als Wahrheitstabelle dokumentiert.
- **Keine Software-Tests auf echter Hardware.** `battery_monitor.py` ist nur syntaktisch geprüft (`py_compile`), die Overlays nur gegen die Dokumentation.
- **Keine thermische Analyse.**

## B) Inbetriebnahme-Messplan (nach dem Löten)

Benötigt: Multimeter. Ideal ist ein Labornetzteil mit Strombegrenzung (3,7 V, 300 mA) statt des Akkus für den ersten Test.

### 1. Ohne Pi, ohne Display, ohne Akku

| # | Messung | Erwartung |
|---|---|---|
| 1.1 | Widerstand TP2 (+5V) ↔ TP4 (GND) | > 1 kΩ (kein Kurzschluss; Elko lädt sich kurz auf) |
| 1.2 | Widerstand TP3 (+3V3) ↔ TP4 | > 1 kΩ |
| 1.3 | Widerstand TP1 (VBAT) ↔ TP4 | ≈ 200 kΩ (R11 + R12) |

### 2. Akku (oder 3,7 V mit Strombegrenzung) am PowerBoost, Pi noch nicht gesteckt

| # | Schalter | Messung | Erwartung |
|---|---|---|---|
| 2.1 | AUS | TP1 (VBAT) | 3,0–4,2 V |
| 2.2 | AUS | TP5 (EN) | **< 0,4 V** (Q1 leitet, Boost aus), TP2 ≈ 0 V |
| 2.3 | EIN | TP5 (EN) | ≈ VBAT, **TP2 = 5,0–5,3 V**, Power-LED leuchtet |
| 2.4 | AUS | Stromaufnahme aus dem Akku | ≈ 25 µA + Eigenverbrauch PowerBoost |
| 2.5 | EIN | J10 Pin 6 (LBO) | ≈ VBAT (Akku nicht leer) |
| 2.6 | – | USB-Netzteil an den PowerBoost | gelbe LED im Fenster „CHG“ leuchtet |

### 3. Abschaltlogik ohne Pi simulieren

| # | Aktion | Erwartung |
|---|---|---|
| 3.1 | Schalter EIN, dann J1 Pin 7 (GPIO4) mit 3,3 V (TP3 geht ohne Pi nicht, externe Quelle) verbinden, Schalter AUS | TP2 bleibt bei 5 V (Q2 hält) |
| 3.2 | GPIO4-Verbindung lösen | TP2 fällt auf 0 V (Q1 schaltet EN ab) |
| 3.3 | Schalter AUS: J1 Pin 36 (GPIO16) gegen GND messen | 0 Ω (Schalter meldet AUS) |

### 4. Mit Pi und Display

| # | Prüfung | Erwartung |
|---|---|---|
| 4.1 | Booten, `vcgencmd get_throttled` | `0x0` (keine Unterspannung) |
| 4.2 | `i2cdetect -y 1` | Gerät an Adresse `48` |
| 4.3 | `cat /dev/shm/battery` | Spannung ±0,05 V zur Multimetermessung an TP1 |
| 4.4 | `evtest`: jede Taste drücken | passende Keycodes laut `setup-guide.md` |
| 4.5 | Ton über Lautsprecher, Lautstärkeknopf drehen | Lautstärke ändert sich |
| 4.6 | Kopfhörer einstecken | Lautsprecher verstummt, Stereo im Kopfhörer |
| 4.7 | Schalter AUS | Pi fährt herunter, ca. 5–15 s später TP2 = 0 V, Power-LED aus |
| 4.8 | Gerät 30 min unter Last (Spiel) | Temperatur `vcgencmd measure_temp` < 80 °C, keine Drosselung |
| 4.9 | UART: Adapter an J8, 115200 Baud | Boot-Meldungen und Login-Prompt |
