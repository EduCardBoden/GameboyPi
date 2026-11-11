# Mechanik / Gehäuse (v1.2)

Quelle: `mechanical/cad-source/gameboy_pi_case.scad` (OpenSCAD 2021.01, parametrisch). Bauteilpositionen kommen aus `design.py`, der Abgleich läuft automatisch über `tools/check_consistency.py`.

## Hauptmaße

| Parameter | Wert | Hinweis |
|---|---|---|
| Außen | 84 × 140 × 29,3 mm, Eckradius 6 mm, Fase 1,2 mm | Original-GBC: 78 × 133,5 × 27,4 mm |
| Wand | 2,0 mm | 5 Perimeter bei 0,4-mm-Düse |
| Platine im Gehäuse | 1 mm Luft je Seite | |
| Trennebene | z = 13,7 mm (Front 13,7 + Rückschale 15,6) | |
| Spiel bewegliche Teile | 0,25 mm (`tol`) | FDM-üblich 0,2–0,3 mm |

## Höhenstapel (z ab Vorderfläche)

| Ebene | z [mm] | Herleitung |
|---|---|---|
| Frontwand innen | 2,0 | `wall` |
| Displayglas vorne | 2,5 | + 0,5 Luft (Moosgummi) |
| Display-Stapel | 9,6 | 1,3 Touch + 0,5 Klebeband + 2,2 LCD + 1,6 Modul + 4,0 Abstandshülse |
| Platine Vorderseite | 12,1 | `z_pcb_front` |
| Platine Rückseite / Trennung | 13,7 | + 1,6 |
| Pi Zero (Platinenoberkante) | 24,7–26,3 | 8,5 Buchse + 2,5 Stiftleiste |
| Rückwand innen | 27,3 | 1,0 mm Luft über dem Pi |

## Tasten (Omron B3F-1020: 6 × 6 × **5,0 mm**, laut Omron-Datenblatt bestätigt)

- Stößellänge = 12,1 − 5,0 − 2,0 − 1,2 (Flansch) − 0,15 = **3,75 mm**
- Leerweg 0,15 mm + Schaltweg 0,25 mm = 0,4 mm ≪ Überstand der Kappe 1,6 mm ✔
- D-Pad: 4 Stößel auf 7,5 mm Radius (per Konsistenzprüfung gegen SW1–SW4 bestätigt), Kipp-Noppe in der Mitte.

## Verschraubung

| Größe | Wert |
|---|---|
| Schraube | M2,5 × 20, selbstschneidend in PLA |
| Kopfauflage | z = 26,3 (Senkung Ø 5,2, 3 mm tief) |
| Schraubenspitze | z = 6,3 |
| Kernloch Frontdom | Ø 2,2 mm, ab z = 3,0 |
| **Einschraubtiefe** | 12,1 − 6,3 = **5,8 mm ≈ 2,3 × d** ✔ (Richtwert ≥ 2 × d in Kunststoff) |
| Domwand | (6,0 − 2,2) / 2 = 1,9 mm |

Alternative bei häufigem Öffnen: Gewindeeinsätze M2,5 (Ø 3,5 mm), dann Dom auf Ø 6,5 und Loch Ø 3,6. Nicht umgesetzt, weil der Probedruck fehlt.

## Akku, Anschlüsse, Wärme

- Akkurahmen innen 54 × 36 mm (Akku 103450 bis 52 × 34 × 10 mm + Schutzplatine), 4 mm hoch, Kabelaussparung unten links. Der Akku ist ohne Werkzeug tauschbar, sobald die Rückschale ab ist.
- Durchgesteckte Beinchen der Front-Bauteile (D1, R1) liegen unter dem Akku: kürzen und mit Kapton abdecken.
- Öffnungen: Micro-USB Laden (unten), Mini-HDMI + Micro-USB Daten (oben), microSD (rechts), Klinke (unten), Lautstärke (links), Schalter (oben), Lichtleiter CHG (hinten).
- 8 Lüftungsschlitze 2,2 × 18 mm über dem Pi.

## Druck

| Teil | Masse (Vollmaterial) | Ausrichtung |
|---|---|---|
| front.stl | 35,7 g | Sichtseite auf dem Bett, keine Stützen |
| back.stl | 43,5 g | Rückseite auf dem Bett, keine Stützen |
| Tasten, Knopf, Hülsen, 4 Logo-Einlagen | 5,8 g | Druckfläche nach unten |
| **Summe** | **85 g** (mit 3 Wänden / 20 % Infill real ≈ 60–70 g) | |

Alle 11 STLs sind geschlossen (0 offene Kanten, `tools/stl_report.py`). Kollisionsprüfung: 21 Hüllkörper, 0 Kollisionen (`build/collision_report.txt`).
Material PLA (matt schwarz + Silk silber/lila), 0,2 mm Schicht, 3 Wände, 20 % Infill. PETG wäre wärmefester (Pi bis ≈ 60 °C Gehäuseinnenluft), passt aber ohne Änderung.

## Nicht umgesetzt / Grenzen

- **STEP des Gehäuses:** OpenSCAD 2021 exportiert kein STEP, FreeCAD ist nicht installiert. Ein aus STL umgewandeltes STEP wäre nur ein Facettenmodell ohne Nutzen für die Weiterkonstruktion. Die Platine liegt als STEP vor (`electronics/assembly/GameboyPi.step`).
- Bauhöhen von PTV09A-2, SJ1-3525N, Elkos und Lautsprecher sind nicht gemessen (README-Risiko 5). Erst die Frontschale probedrucken.
