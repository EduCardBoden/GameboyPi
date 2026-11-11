# Architektur: wie die Daten fließen

GameboyPi besteht aus drei Teilen, die über **Koordinaten und Netznamen** gekoppelt sind: Platine (Python → KiCad), Gehäuse (OpenSCAD) und Pi-Software. Elektrische und mechanische Details: [documentation/wiring.md](documentation/wiring.md).

## 1. Platine: `electronics/kicad-project/`

```
design.py ──► make_sch.py ──► GameboyPi.kicad_sch ──► check_netlist.py (Netzliste == design.py?)
   │               └──► build/sch_info.json (Symbol-UUIDs)
   │                          │
   └──────────────► make_pcb.py ──► GameboyPi.kicad_pcb (platziert, ohne Bahnen)
                                          │
                               route.py (Freerouting 2.5, bis zu 4 Durchläufe)
                                          │
                     kicad-cli: ERC/DRC ──► build/erc.rpt, build/drc.rpt
                                Gerber/Bohrdaten ──► ../gerber/ + ../../bestellung/1_platine_JLCPCB/
                                BOM, Pick&Place, PDFs, Renderings, STEP ──► ../assembly/, ../schematics/
```

| Datei | Aufgabe | Liest | Schreibt |
|---|---|---|---|
| `design.py` | **Einzige Quelle** für Bauteile, Pins→Netze, Positionen, Seite, Platinenmaße, Leistungsnetze | – | – (wird importiert) |
| `make_sch.py` | Schaltplan aus Bibliothekssymbolen. Alle Verbindungen laufen über globale Labels, Anordnung nach `group` | `design.py`, KiCad-Symbolbibliothek | `.kicad_sch`, `build/sch_info.json` |
| `check_netlist.py` | Exportiert die Netzliste und vergleicht sie mit `design.py`. **Bricht den Build bei Abweichung ab** | `.kicad_sch` | `build/GameboyPi.net` |
| `make_pcb.py` | Platine: Netzklassen, Footprints, Umriss, Beschriftung, GND-Flächen, Sperrflächen am Rand, DRC-Ausnahmen | `design.py`, `sch_info.json`, Footprint-Bibliothek | `.kicad_pcb`, `.kicad_pro` |
| `route.py` | Autorouting. Exportiert eine eingerückte Kontur, löscht Bahnen in der Randzone und routet sie neu, verbreitert Engstellen auf 0,15 mm | `.kicad_pcb` | `.kicad_pcb`, `build/*.dsn/.ses` |
| `build.ps1` | Ruft alles der Reihe nach auf. Bricht beim ersten Fehler ab (Exit-Code), fasst ERC/DRC zusammen | – | alle Exporte |

**Nicht deterministisch:** Freerouting liefert bei jedem Lauf ein anderes Layout. Darum ist die Platine nach jedem Build neu zu prüfen (DRC + Sichtprüfung).

## 2. Gehäuse: `mechanical/cad-source/`

`gameboy_pi_case.scad` ist eine einzige parametrische Datei. Der Parameter `part` wählt aus, was gebaut wird (`front`, `back`, Tasten, Logo-Einlagen, `check`, `showcase` …). `build.ps1` ruft OpenSCAD einmal pro Teil auf:

1. **Kollisionsprüfung:** jeder Bauteil-Hüllquader (`part="check"`, `check_idx=n`) gegen beide Schalen, 8 Prozesse parallel. Ergebnis in `build/collision_report.txt`.
2. **STL-Export** nach `../stl/`, danach Kopie nach `bestellung/3_3d_druck/`.
3. **Vorschaubilder** nach `../previews/`.

Das Logo kommt aus `logo/trace_logo.py` (Bild → `logo/gbx_logo.scad`). Das ist nur nötig, wenn sich das Logo-Bild ändert.

### Kopplung Platine ↔ Gehäuse (Achtung)

Die Bauteilpositionen im Abschnitt „Bauteil-Positionen (aus design.py)“ der `.scad` sind **von Hand übertragen**: Bohrungen, Tasten, LED, Schalter, Klinke, Poti, Display. Wer in `design.py` etwas verschiebt, muss die `.scad` nachziehen und die Kollisionsprüfung laufen lassen. Seit v1.2 prüft **`tools/check_consistency.py`** den Abgleich automatisch (Positionen und alle GPIOs in `config.txt.append`, `install.sh`, `battery_monitor.py`). VS-Code-Task „Konsistenz prüfen“.

## 3. Software: `software/`

Die Rechenlogik von `battery_monitor.py` ist ohne Pi testbar: `python -m pytest software/tests -q`. `configuration/install.sh` läuft auf dem Pi (RetroPie 4.8). Es ergänzt `/boot/config.txt` (Overlays für Tasten, Audio, Abschaltlogik), baut fbcp-ili9341 und installiert den Akku-Dienst `battery_monitor.py` (ADS1115 + LBO → `/dev/shm/battery`, Abschaltung bei leerem Akku). Die GPIO-Belegung muss zu `PI_PINS` in `design.py` passen.
