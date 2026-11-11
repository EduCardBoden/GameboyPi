# Projektübersicht GameboyPi v1.2

Handheld im Game-Boy-Color-Stil: Raspberry Pi Zero 2 W auf einer eigenen Trägerplatine (KiCad, per Skript erzeugt) in einem 3D-gedruckten Gehäuse (OpenSCAD), LiPo-Akku, RetroPie.
**Status 11.11.2026:** Design vollständig, alle Rechner-Prüfungen bestanden (ERC, DRC, Netzliste, Kollision, Konsistenz, Unit-Tests). **Nicht gebaut, nicht gemessen.**

## Kennzahlen

| | |
|---|---|
| Rechner | Pi Zero 2 W (Zero W kompatibel), kopfüber auf 2×20-Buchse, Rückseite |
| Display | 2,4" ILI9341 SPI 320×240 (LAFVIN ≈ MSP2402), fbcp-ili9341, 60 fps |
| Bedienung | D-Pad, A, B, Start, Select (8 × Omron B3F-1020), Ein/Aus-Schiebeschalter, Lautstärkepoti |
| Energie | LiPo 103450 2000 mAh → PowerBoost 1000C (5,2 V, 1 A, Load-Sharing), Soft-Power mit 2 × BS170 |
| Audio | PWM GPIO12/13 → RC-Filter → Klinke (Kopfhörer) bzw. PAM8302 → 20-mm-Lautsprecher (≤ 0,5 W) |
| Akkuüberwachung | ADS1115 an VBAT/2 + PowerBoost-LBO an GPIO20 → `battery_monitor.py` |
| Platine | 78 × 134 mm, 2 Lagen, 1,6 mm FR-4, 35 µm Cu, nur THT + Module |
| Gehäuse | 84 × 140 × 29,3 mm, PLA, 11 Druckteile, ≈ 85 g |
| Laufzeit | ≈ 2,1 h typisch (1,5–2,7 h), Rechnung in `battery-runtime.md` |
| Kosten | ≈ 150–190 € je nach Bezugsweg, siehe `PURCHASING_COMPARISON.md` |

## Dokumente

| Datei | Inhalt |
|---|---|
| [HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md) | Blockschaltbild, Spannungen, Ströme, Schnittstellen |
| [PCB_DESIGN.md](PCB_DESIGN.md) | Platinendaten, Regeln, Leiterbahnberechnung, Auslegungsrechnungen v1.2 |
| [MECHANICAL_DESIGN.md](MECHANICAL_DESIGN.md) | Gehäusemaße, Stapelhöhen, Schrauben, Toleranzen, Druck |
| [FIRMWARE_ARCHITECTURE.md](FIRMWARE_ARCHITECTURE.md) | Pi-Software: Overlays, Treiber, Akku-Dienst, Tests |
| [FINAL_BOM.md](FINAL_BOM.md) | Endgültige Stückliste mit Herstellernummern |
| [PURCHASING_COMPARISON.md](PURCHASING_COMPARISON.md) | Preis- und Lieferprüfung vom 11.11.2026, Einkaufsweg |
| [ASSEMBLY_GUIDE.md](ASSEMBLY_GUIDE.md) | Montage-Checkliste (Details: `assembly-guide.md`) |
| [TESTING_PLAN.md](TESTING_PLAN.md) | Prüfstrategie (Ergebnisse und Messplan: `testing.md`) |
| [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) | Offene Punkte, nächste Versionen |
| `wiring.md`, `battery-runtime.md`, `assembly-guide.md`, `testing.md` | Bestehende Detaildokumente (v1.1, auf v1.2 nachgeführt) |
| [project-log/](project-log/) | Aktivitätslog, Entscheidungen, Changelog, Quellen, Testergebnisse |
| `final-report/GameBoy_Project_Engineering_Documentation.docx` (+ `.pdf`) | Abschlussbericht (Word, 16 Seiten). Neu erzeugen: `tools/make_report.py`, dann `tools/finalize_report.ps1` |

## Wichtige Dateien

| Was | Wo |
|---|---|
| Einzige Quelle der Elektronik | `electronics/kicad-project/design.py` |
| Gehäuse (parametrisch) | `mechanical/cad-source/gameboy_pi_case.scad` |
| Fertigungsdaten | `electronics/gerber/GameboyPi_Gerber.zip` (= `bestellung/1_platine_JLCPCB/`) |
| Druckdaten | `mechanical/stl/*.stl` (= `bestellung/3_3d_druck/`) |
| Pi-Konfiguration | `software/configuration/` |
| Prüfwerkzeuge | `tools/check_consistency.py`, `tools/stl_report.py`, `software/tests/` |
