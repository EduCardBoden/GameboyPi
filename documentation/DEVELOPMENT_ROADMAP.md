# Roadmap

## Erledigt in v1.2 (11.11.2026)
- R6/R7 47 kΩ (Lautsprecher ≤ 0,5 W, PowerBoost-Spitzenlast < 1 A)
- R10 100 kΩ + GPIO20 ohne Pull (LBO in TPS61090-Spezifikation)
- Abschaltlogik rechnerisch nachgewiesen (EN-Pull-up 200 kΩ, BS170 bei 1 mA spezifiziert)
- `battery_monitor.py`: ADC-Lastkorrektur, Kalibrierfaktor, LBO-Entprellung, 7 Unit-Tests
- `install.sh` robust und mehrfach ausführbar
- `tools/check_consistency.py` (Platine ↔ Gehäuse ↔ Software), `tools/stl_report.py`
- Bestückungsdruck v1.2, Lautsprechertext nicht mehr über Pads
- Dokumentation, Projekt-Log, Word-Bericht

## Nächste Schritte (v1.2 bauen)
1. Teile bestellen (Pi-Lieferlage prüfen), Platinen bestellen
2. Frontschale probedrucken, Bauhöhen von Poti, Klinke, Elkos, Lautsprecher messen, ggf. `.scad` anpassen
3. Aufbau und Messplan (`testing.md` B) abarbeiten, Ergebnisse in `project-log/TEST_RESULTS.md`

## v1.3 (nach den ersten Messungen)
| Idee | Nutzen | Voraussetzung |
|---|---|---|
| Akkuanzeige im Bild (pngview-Overlay aus `/dev/shm/battery`) | Bedienkomfort | läuft auf echter Hardware |
| Gewindeeinsätze M2,5 statt selbstschneidender Schrauben | häufiges Öffnen | Probedruck |
| USB-C-Ladebuchse (PowerBoost hat Micro-USB) | zeitgemäßer Stecker | anderes Lademodul oder USB-C-Adapterplatine |
| Manuelles Routing der Audio-/SPI-Bereiche | weniger Übersprechen | Messung des Rauschens |
| Schultertasten L/R (GPIO 7, 18, 21 frei) | SNES/GBA-Spiele | neue Taster am Rand + Gehäuse |
| Gehäuse-STEP über FreeCAD/CadQuery | Austausch mit anderen CAD-Systemen | Werkzeugwechsel |

## Experimentell
- Raspberry Pi OS Bookworm mit `mipi-dbi-spi` statt fbcp-ili9341 (aktueller Kernel, aber langsamer)
- I2S-DAC statt PWM-Audio (rauschärmer, braucht Platinenänderung)
