# Platinenentwurf (v1.2)

Quelle: `electronics/kicad-project/design.py` → `make_sch.py` / `make_pcb.py` / `route.py` (Freerouting 2.5) → `build.ps1`. Nie die `.kicad_*`-Dateien von Hand ändern.

## Platinendaten

| Parameter | Wert |
|---|---|
| Maße | 78 × 134 mm, Eckradius 3 mm |
| Lagen | 2 (F.Cu, B.Cu), GND-Fläche auf beiden Seiten |
| Material / Dicke | FR-4, 1,6 mm (Gehäuse ist auf 1,6 mm ausgelegt) |
| Kupfer | 1 oz = 35 µm außen |
| Oberfläche | bleifreies HASL |
| Bestückung | nur THT + Module, Handlötung |
| Montage | 4 × M2,5 (Ø 2,7 mm) an (4,4), (74,4), (4,130), (74,130) |

## Regeln (Netzklassen, `make_pcb.py`)

| Klasse | Netze | Bahnbreite | Abstand | Via |
|---|---|---|---|---|
| Default | Signale | ≥ 0,15 mm (meist 0,25) | 0,2 mm | 0,6 / 0,3 mm |
| Power | +5V, GND, VBAT | 1,0 mm (Engstellen ≥ 0,75 mm) | 0,25 mm | 0,8 / 0,4 mm |
| Power3V3 | +3V3 | 0,5 mm | 0,25 mm | 0,8 / 0,4 mm |
| Randzone | – | keine Bahnen/Vias im 1-mm-Rand | – | – |

Fertigbarkeit (JLCPCB-Standard): min. Bahn/Abstand 0,127 mm, min. Bohrung 0,3 mm → eingehalten (kleinste Bohrung 0,30 mm, 25 Vias).

## Strombelastbarkeit (IPC-2221, Außenlage, 35 µm)

I = 0,048 · ΔT^0,44 · A^0,725 (A in mil²)

| Breite | ΔT 10 K | ΔT 20 K | Verwendung (gemessen im Layout v1.2) |
|---|---|---|---|
| 0,25 mm | 0,88 A | 1,19 A | Signale (< 10 mA) |
| 0,38 mm | 1,18 A | 1,59 A | engste Stelle +3V3 (Last ≈ 0,15 A) |
| 0,50 mm | 1,45 A | 1,96 A | +3V3 regulär |
| 0,75 mm | 1,94 A | 2,63 A | engste Stelle +5V/GND/VBAT |
| 1,00 mm | 2,39 A | 3,24 A | +5V/GND regulär |

Spitzenlast +5V ≈ 0,84 A (siehe HARDWARE_ARCHITECTURE.md) → Reserve ≥ 2,3 × bei 10 K. VBAT führt auf der Platine nur µA (der Akkustrom fließt im PowerBoost).

## Auslegungsrechnungen v1.2

### 1. Lautsprecherleistung begrenzen (R6/R7: 10 kΩ → 47 kΩ)

- Pi-PWM-Ausgang nach dem Filter: 3,3 V · 150/(270+150) = 1,18 V_ss → **0,417 V_eff** Vollaussteuerung.
- Mischnetz: zwei Kanäle über R6/R7 auf RV1 (10 kΩ, Schleifer oben). Thevenin: U = 0,417 · 10k/(10k + R/2), R_i = (R/2) ‖ 10k.
- PAM8302: feste **24 dB = ×15,85**, Trimmpoti auf dem Modul, Eingangswiderstand ≥ 10 kΩ (Datenblatt Diodes Inc., Adafruit). Ausgang klippt bei 5 V an 8 Ω bei ≈ 3,5 V_eff (Adafruit: 1,5 W @ 10 % THD).
- Lautsprecher PUI AS02008MR-5-R: **0,5 W Nenn-, 0,8 W Maximalleistung**, 8 Ω → max. 2,0 V_eff.

| R6/R7 | P bei R_ein = 10 kΩ | P ohne Last (schlechtester Fall) |
|---|---|---|
| 10 kΩ (v1.1) | 1,36 W | 1,53 W (geklippt) → **Lautsprecher überlastet** |
| 22 kΩ | 0,53 W | 1,24 W |
| 33 kΩ | 0,29 W | 0,78 W |
| **47 kΩ (v1.2)** | **0,17 W** | **0,49 W** ✔ |

47 kΩ hält die Nennleistung auch dann ein, wenn der Verstärkereingang höherohmig ist als angenommen. 0,17 W entsprechen bei typ. 88 dB/0,1 W/0,1 m etwa 90 dB in 10 cm, das reicht für ein Handgerät. Nebeneffekt: Audio-Spitzenstrom am 5-V-Netz ≈ 120 mA statt ≈ 330 mA.

### 2. LBO-Strom (R10: 10 kΩ → 100 kΩ)

- TPS61090-LBO ist Open-Drain, spezifiziert mit **100 µA** Low-Strom (V_OL ≤ 0,4 V).
- v1.1: (3,3 V − 0,25 V) / 10 kΩ = 0,31 mA + Pi-Pull-up (≈ 50 kΩ → 66 µA) = **0,37 mA** → 3,7 × über der Spezifikation.
- v1.2: 3,05 V / 100 kΩ = **31 µA**, interner Pull an GPIO20 abgeschaltet (`gpio=20=ip,pn`, `PUD_OFF`) ✔.
- Low-Pegel an GPIO20 ≈ V_F(BAT85 bei 31 µA, ≈ 0,2 V) + V_OL(≤ 0,4 V) ≤ 0,6 V < V_IL des Pi (0,8 V) ✔.

### 3. Akkuspannungsmessung

ADS1115-Gleichtakt-Eingangsimpedanz bei ±4,096 V: **6 MΩ** (TI). Teiler effektiv 100k / (100k ‖ 6M) → Faktor **2,0167** statt 2,000 (−0,8 %, ≈ −35 mV bei 4,2 V). Wird in `battery_monitor.py` herausgerechnet, statt Bauteile zu ändern. C6 100 nF puffert den Abtastkondensator.

## Prüfergebnisse (finaler Build vom 11.11.2026, 20:17, Schaltplan Rev 1.2)

| Prüfung | Ergebnis |
|---|---|
| Netzliste Schaltplan ↔ design.py | keine fehlenden/zusätzlichen Verbindungen |
| ERC (alle Schweregrade) | 0 Fehler, 0 Warnungen |
| DRC inkl. Schaltplan-Parität | **0 Fehler**, 0 unverbundene Pads, 0 Paritätsfehler, 101 Warnungen (65 silk_overlap, 26 silk_over_copper, 8 silk_edge_clearance, 2 starved_thermal) |
| Routing | 604 Bahnen, 25 Vias, 0 ungeroutet; +5V ≥ 1,0 mm, GND/VBAT ≥ 0,75 mm, +3V3 ≥ 0,38 mm |
| Bohrdaten | PTH 206 Bohrungen (0,3–2,3 mm), NPTH 16 (1,2–3,2 mm) |
| Gerber-Paket | 12 Dateien, Zip identisch mit `bestellung/1_platine_JLCPCB/` (MD5 4f6c694a…) |

**Hinweis:** Freerouting erzeugt bei jedem Build ein anderes Layout. Darum vor der Bestellung die Gerber im Hersteller-Viewer ansehen.

## Fertigungsdateien

`electronics/gerber/` (Gerber X2, Excellon, Job-Datei, Zip) · `electronics/assembly/` (Bestückungspläne PDF, Pick&Place, KiCad-BOM, STEP der Platine, 3D-Bilder) · `electronics/schematics/GameboyPi_Schaltplan.pdf`.
