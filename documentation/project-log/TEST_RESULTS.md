# Testergebnisse

Alle Tests auf dem Entwicklungs-PC (Windows 11). **Keine physischen Tests** – es gibt noch keine Hardware.

| # | Test | Datum / Zeit | Werkzeug + Konfiguration | Ergebnis | Fehler → Lösung | Offen |
|---|---|---|---|---|---|---|
| T1 | Netzliste Ausgangsstand | 11.11. 19:56 | `check_netlist.py` (KiCad 10.0.6) | keine / keine | – | – |
| T2 | ERC Ausgangsstand | 19:56 | `kicad-cli sch erc --severity-all` | 0 / 0 | – | – |
| T3 | DRC Ausgangsstand | 19:56 | `kicad-cli pcb drc --severity-all --schematic-parity` | 0 Fehler, 105 Warn., 0 unverbunden, Parität 0 | – | – |
| T4 | Netzliste nach R-Änderung | 20:01 | wie T1 | keine / keine | – | – |
| T5 | PCB-Build 1 | 20:02 | `build.ps1` (Freerouting 2.5) | ERC 0/0, DRC 0 Fehler/102 Warn., 0 ungeroutet | Silk „v1.1“, Text über Pads → make_pcb.py | – |
| T6 | Unit-Tests battery_monitor | 20:03 | pytest 9.2, Python 3.11 | 1. Lauf 6/7 | `divider_factor(inf)` = NaN → Leitwertformel | – |
| T7 | Unit-Tests | 20:03 | wie T6 | 2. Lauf 6/7 | Rundung 2,0000000000000004 → Test mit Toleranz | – |
| T8 | Unit-Tests | 20:04 | wie T6 | **7/7 bestanden** | – | – |
| T9 | Syntax `battery_monitor.py` | 20:04 | `py_compile` | ok | – | – |
| T10 | PCB-Build 2 | 20:04 | `build.ps1` | 0 Fehler, 101 Warn. | Text berührt Loch H5 → x = 59,5 | – |
| T11 | Syntax `install.sh` | 20:05 | `bash -n` (Git Bash) | ok | – | – |
| T11b | Statische Analyse `install.sh` | 20:45 | ShellCheck 0.11.0, `-s bash` | **0 Befunde** | – | – |
| T12 | Konsistenz | 20:05 | `tools/check_consistency.py` | 36 Prüfungen, 0 Abweichungen | – | – |
| T13 | Mutationstest Konsistenz | 20:05 | 3 Fehler injiziert (btn_a, GPIO Taste A, RST-Pin) | 3/3 erkannt, Exit 1 | – | – |
| T14 | PCB-Build 3 | 20:06 | `build.ps1` | **ERC 0/0; DRC 0 Fehler, 0 unverbunden, 101 Warn. (65 silk_overlap, 26 silk_over_copper, 8 silk_edge_clearance, 2 starved_thermal); 602 Bahnen, 30 Vias, 0 ungeroutet** | Schaltplan-Schriftfeld noch Rev 1.1 → make_sch.py | – |
| T14b | **PCB-Build 4 (final)** | 20:17 | `build.ps1` | **ERC 0/0; DRC 0 Fehler, 0 unverbunden, 101 Warn. (65/26/8/2); 604 Bahnen, 25 Vias, 0 ungeroutet** | – | Gerber vor Bestellung ansehen |
| T15 | Gerber-Paket | 20:07 | MD5 | `electronics/gerber/…zip` = `bestellung/…zip` (4f6c694a…, Build 4) | – | – |
| T16 | Bahnbreiten | 20:07 | pcbnew-Skript | Build 4: +5V ≥ 1,00, GND ≥ 0,75, +3V3 ≥ 0,38 (1,18 A zulässig), VBAT ≥ 0,75 mm | – | – |
| T17 | Bohrdaten | 20:10 | Excellon-Auswertung | Build 4: PTH 206 (min. 0,30 mm), NPTH 16 | – | – |
| T18 | STL-Geometrie | 20:10 | `tools/stl_report.py` | 11/11 geschlossen, 85 g PLA Vollmaterial | – | – |
| T19 | Kollisionsprüfung Gehäuse | 21.10.2026 (übernommen) | OpenSCAD, 21 Hüllkörper | 0 Kollisionen | – | gilt, da `.scad` unverändert |
| T20 | Word-Bericht | 20:40 | python-docx 1.2 + Microsoft Word (COM: TOC-Update, SaveAs2, PDF-Export), Seiten-Rendering per WinRT | öffnet in Word, 16 Seiten, TOC mit Seitenzahlen, alle Seiten gesichtet | 4 Darstellungsfehler → behoben, siehe ACTIVITY_LOG | – |
| T21 | Gehäuse-STEP | 20:50 | FreeCAD 1.1.4, `tools/scad_to_step.py` | 11/11 gültig und geschlossen, Volumen = STL ± 0,004 % | CSG-Import gescheitert → STL-Weg | Rundungen facettiert |
| T22 | STEP-Rücklesetest | 20:52 | FreeCAD `Part.read` | front 84,0 × 140,0 × 13,7 mm, back 84,0 × 140,0 × 15,6 mm, gültig | – | – |
| T23 | Software-Tests mit installiertem Python | 20:45 | Python 3.13.17, pytest 9.2.0 | 7/7 | – | – |
| T24 | `build.ps1` (Gehäuse) nach Änderung | 20:58 | PowerShell-Parser + STEP-Block einzeln | 0 Parserfehler, 11/11 STEP | Steuerzeichen im Pfad → korrigiert | voller Gehäuse-Build (25 min) nicht nötig, `.scad` unverändert |

## Noch offen (physisch)
Messplan `documentation/testing.md` Teil B (1.1–4.9 und 4.5b), Probedruck, Laufzeitmessung, Thermik, Lautstärke.
