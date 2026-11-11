# Aktivitätslog

Zeiten MEZ. Werkzeuge: KiCad 10.0.6 (kicad-cli, pcbnew-Python), Freerouting 2.5, OpenSCAD 2021.01, Python 3.11 (KiCad), pytest 9.2, pypdf, python-docx, Git, Firecrawl (Web-Recherche).

## 2026-11-11 – Engineering-Durchlauf v1.2

| Zeit | Tätigkeit | Ergebnis / Dateien |
|---|---|---|
| 19:53 | Bestandsaufnahme: CLAUDE.md, README, ARCHITECTURE, design.py, make_*.py, .scad, build-Skripte, Software, BOM, Bestellpaket, Berichte | Projekt ist ein **Pi-Zero-2-W-Handheld, kein AVR/Arduino**. Der Missionstext wurde darauf übertragen („Firmware“ = Pi-Konfiguration + Python-Dienst) |
| 19:55 | Werkzeuge geprüft | kicad-cli 10.0.6 ✔, OpenSCAD ✔, Word ✔, Node ✔, FreeCAD ✗ (nicht installiert, nicht nachinstalliert, siehe Entscheidung E7) |
| 19:56 | Git-Sicherung: Branch `engineering-v1.2`, Tag `baseline-v1.1` | Originalstand jederzeit wiederherstellbar |
| 19:56 | Ausgangsprüfung (ohne Änderung) | Netzliste keine/keine, ERC 0/0, DRC 0 Fehler, 105 Warnungen, 0 unverbunden, Parität 0 |
| 19:57 | Leiterbahnbreiten je Netz ausgemessen (pcbnew-Skript) | +5V min. 0,75 mm (Doku sagte 1,0 mm → korrigiert), +3V3 0,38 mm |
| 19:58 | Datenblätter: Omron B3F, PUI AS02008MR-5-R, PAM8302A, Adafruit PAM8302/PowerBoost, BS170 | B3F-1020 5,0 mm ✔; Lautsprecher 0,5 W / max. 0,8 W; PAM8302 24 dB + Trimmpoti; BS170 Vth bei 1 mA |
| 19:59 | Adafruit-Eagle-Schaltplan PowerBoost Rev B ausgewertet | EN-Pull-up R13 = 200 kΩ an VBAT → Risiko 2 rechnerisch geklärt |
| 20:00 | TI TPS61090-Datenblatt | **Befund:** LBO darf max. 100 µA ziehen, R10 = 10 kΩ zog ≈ 0,37 mA |
| 20:01 | Rechnung Audio-Pegel | **Befund:** Lautsprecher kann mit 1,4 W (2,7 × Nennleistung) betrieben werden |
| 20:01 | `design.py`: R10 → 100k, R6/R7 → 47k; Schaltplan neu, Netzlistencheck | keine/keine |
| 20:02 | PCB-Build 1 | ERC 0/0, DRC 0 Fehler/102 Warn., 0 ungeroutet |
| 20:02 | TI ADS1115-Datenblatt | 6 MΩ Eingangsimpedanz → −0,8 % Messfehler |
| 20:03 | `battery_monitor.py` überarbeitet, 7 Unit-Tests geschrieben | 1. Lauf: 1 Fehler (inf/inf = NaN im Teilerfaktor) → Formel korrigiert; 2. Lauf: Rundung im Test → Toleranz; 3. Lauf 7/7 ✔ |
| 20:03 | Rendering geprüft: Bestückungsdruck „v1.1“, Lautsprechertext über Pads | `make_pcb.py`: v1.2, Text verschoben |
| 20:04 | PCB-Build 2 | 0 Fehler, 101 Warnungen; Text berührt H5 → nochmals verschoben |
| 20:04 | `config.txt.append` (gpio=20=ip,pn), `install.sh` (robust) | `bash -n` ok, LF erhalten |
| 20:05 | `tools/check_consistency.py` geschrieben | 36 Prüfungen, 0 Abweichungen; Mutationstest mit 3 eingebauten Fehlern → alle 3 erkannt |
| 20:06 | PCB-Build 3 | ERC 0/0, DRC 0 Fehler, 101 Warn., 0 unverbunden, 602 Bahnen, 30 Vias; Gerber-Zip = Bestellpaket |
| 20:06 | Preisrecherche BerryBase.at, Reichelt, Kiwi, Botland, raspberry.tips | Pi Zero 2 W und PowerBoost bei BerryBase nicht lieferbar; ADS1115 lieferbar |
| 20:10 | Bohrdaten ausgewertet | PTH 211 (0,3–2,3 mm), NPTH 16 |
| 20:10 | `tools/stl_report.py` geschrieben und ausgeführt | 11/11 STLs geschlossen, 85 g |
| 20:12 | Bestehende Doku nachgeführt: README, testing.md, wiring.md, battery-runtime.md, setup-guide.md, ARCHITECTURE.md, CLAUDE.md, BOM-CSV, DigiKey-CSV, Einkaufsliste, VS-Code-Tasks | |
| 20:15 | Neue Doku in `documentation/` + `project-log/` | siehe CHANGELOG |
| 20:16 | Schaltplan-PDF zu PNG gerendert (WinRT) | Schriftfeld zeigte Rev 1.1 / 2026-10-20 → `make_sch.py` Rev 1.2 / 2026-11-11 (von PowerShell eingefügtes Byte-Order-Mark wieder entfernt) |
| 20:17 | PCB-Build 4 (final) | ERC 0/0, DRC 0 Fehler/101 Warn., 0 unverbunden, 604 Bahnen, 25 Vias, PTH 206; Gerber-Zip = Bestellpaket (MD5 4f6c694a) |
| 20:18–20:40 | Word-Bericht: `tools/make_report.py` (python-docx) + `tools/finalize_report.ps1` (Word aktualisiert TOC, exportiert PDF) | 16 Seiten, 5 Abbildungen, 20 Tabellen. Probleme: Word hängt unsichtbar beim Öffnen direkt aus Dokumente und bei `Save()` im Kompatibilitätsmodus → Temp-Kopie + `SaveAs2` + 120-s-Watchdog (Nachtrag 21:05: SaveAs2 stellte den Kompatibilitätsmodus entgegen meiner Annahme **nicht** um; jetzt setzt `make_report.py` Modus 15 direkt in settings.xml, geprüft); hängende eigene Word-Prozesse beendet. Sichtprüfung aller Seiten als PNG: wörtliche `**` in Zellen, falsche Bildunterschrift, Querverweis, Fußzeilengröße → korrigiert |

## 2026-11-11 – Nachtrag: Werkzeuge installieren (Auftrag „installiere alles was du installieren musst“)

| Zeit | Tätigkeit | Ergebnis |
|---|---|---|
| 20:42 | Bestand geprüft: kein eigenständiges Python (nur MSYS2 ohne pip + KiCad-Python), kein FreeCAD, kein shellcheck, kein pdftoppm | |
| 20:43 | winget: Python 3.13.17, ShellCheck 0.11.0, Poppler 25.07.0 (Benutzerinstallation), FreeCAD 1.1.4 | alle „Successfully installed“; PATH: Python313 steht vor MSYS2 |
| 20:44 | pip: python-docx, pypdf, pytest, fonttools | Import-Test ok |
| 20:45 | Funktionstest | shellcheck `install.sh`: **0 Befunde**; pytest 7/7; Konsistenz 0 Abweichungen; FreeCAD 1.1.4 startet |
| 20:46 | STEP über FreeCAD-CSG-Import versucht | gescheitert („Input shape is null“ bei offset/circle-Extrusionen) → verworfen |
| 20:50 | `tools/scad_to_step.py` (STL → B-Rep → STEP) | 11/11 Teile gültig, Volumenabweichung ≤ 0,004 %, Rücklesetest Front/Rückschale ok |
| 20:55 | In Build, Tasks, Hook und `.gitignore` eingebunden | Fehler beim Einfügen: Git-Bash-Heredoc halbierte Backslashes (`\b` in `1.1\bin` wurde zum Steuerzeichen im FreeCAD-Pfad von `build.ps1`) → Zeile mit `chr(92)` neu geschrieben, Parser 0 Fehler, Block einzeln ausgeführt ok |

## Nicht erledigt
- Physischer Aufbau, Messungen, Probedruck (keine Hardware vorhanden)
- JLCPCB-Preis (Rechner nicht abfragbar), Neuprüfung der DigiKey-Kleinteilpreise
- Kein neuer Gehäuse-Build nötig: `.scad` unverändert, Kollisionsbericht vom 21.10.2026 gilt weiter
