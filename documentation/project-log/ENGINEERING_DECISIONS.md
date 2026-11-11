# Technische Entscheidungen (v1.2)

## E1 – Lautsprecherleistung begrenzen: R6/R7 = 47 kΩ
- **Problem:** PAM8302 (24 dB) liefert an 8 Ω bis ≈ 1,4 W, der Lautsprecher verträgt 0,5 W (max. 0,8 W). Der Audio-Spitzenstrom belastet außerdem den PowerBoost (Risiko 4).
- **Alternativen:** (a) Trimmpoti auf dem Modul zurückdrehen, (b) Software-Grenze, (c) größere Mischwiderstände, (d) stärkerer Lautsprecher.
- **Vergleich:** (a) und (b) lassen sich verstellen bzw. hängen von der Software ab. (d) braucht neue Mechanik. (c) ist fest verdrahtet, kostet nichts und ändert nur Werte.
- **Entscheidung:** (c) 47 kΩ. Damit bleiben auch im ungünstigsten Fall (Verstärkereingang ohne Last) 0,49 W.
- **Vorteile:** Lautsprecher sicher, Spitzenstrom −210 mA. **Nachteile:** etwas leiser (typ. 0,17 W, rechnerisch ≈ 90 dB in 10 cm). Für mehr Lautstärke einen 1-W-Lautsprecher und 33 kΩ nehmen.

## E2 – LBO-Pull-up: R10 = 100 kΩ, interner Pull aus
- **Problem:** Der TPS61090-LBO ist für 100 µA spezifiziert, die Schaltung zog 0,37 mA.
- **Alternativen:** (a) 100 kΩ + Pull aus, (b) Transistorstufe, (c) Spannungsteiler statt Diode.
- **Entscheidung:** (a). Gleiche Bauform, ein Wert weniger in der Stückliste (100 kΩ gibt es schon).
- **Nachteil:** hochohmiger Knoten, darum entprellt die Software.

## E3 – ADC-Lastfehler in Software korrigieren
- **Problem:** 6 MΩ ADC-Eingang am 100-kΩ-Teiler → −0,8 %.
- **Alternativen:** kleinerer Teiler (z. B. 10k/10k → 210 µA Dauerverlust), Puffer-OpAmp, Softwarekorrektur.
- **Entscheidung:** Software (Faktor 2,0167 + `VBAT_CAL`). Kein Mehrverbrauch, keine Platinenänderung.

## E4 – LBO entprellen (3 × 5 s)
- **Problem:** Eine einzelne Low-Messung fuhr sofort herunter. Unter Last sinkt VBAT kurz.
- **Entscheidung:** 3 Messungen in Folge. 15 s Verzögerung sind bei 3,2 V Restspannung unkritisch (PCM im Akku schützt zusätzlich).

## E5 – BS170 beibehalten
- **Problem:** README-Risiko 2 (Schwelle max. 3,0 V bei VBAT ab 3,0 V).
- **Analyse:** Die Schwelle ist bei 1 mA spezifiziert, gebraucht werden 21 µA (EN-Pull-up 200 kΩ). Ein Logic-Level-MOSFET in TO-92 mit gleicher Pinfolge ist kaum erhältlich.
- **Entscheidung:** beibehalten, Restrisiko über Messplan 2.2 abdecken.

## E6 – Architektur nicht neu entwerfen
- **Problem:** Der Missionstext verlangt eine Neukonstruktion von Platine und Gehäuse.
- **Analyse:** Das Design besteht alle Prüfungen. Eine Neukonstruktion ohne Messdaten würde Risiko hinzufügen, aber keine Information. Die fehlenden Daten (Bauhöhen, echte Ströme) gibt es nur durch einen Aufbau.
- **Entscheidung:** gezielte, rechnerisch begründete Korrekturen (E1–E4), Neukonstruktion erst nach dem Prototyp (Roadmap).

## E7 – Gehäuse-STEP
- **Problem:** STEP-Export gefordert. OpenSCAD 2021 kann das nicht.
- **Alternativen:** FreeCAD installieren (≈ 1 GB) und STL → STEP wandeln, CadQuery, OpenSCAD-Nightly.
- **Analyse:** Ein aus dem STL gewandeltes STEP ist ein Facettenmodell ohne Nutzen für die Weiterkonstruktion. Echte B-Rep-STEPs erfordern einen Neuaufbau in einem anderen CAD.
- **Entscheidung (Stand 1):** nicht umgesetzt.
- **Revision 11.11.2026, 20:45:** Auf Wunsch des Users wurde FreeCAD 1.1.4 installiert. Der direkte CSG-Import ließ sich nicht verwenden (Extrusionen von `offset()`/`circle()` liefern leere Formen). Umgesetzt wurde STL → B-Rep → `removeSplitter` → Volumenkörper → STEP. Damit liegen maßhaltige, gültige Volumenkörper vor (Volumenabweichung ≤ 0,004 %) mit facettierten Rundungen. Ein echtes Feature-Modell bliebe ein Neuaufbau in FreeCAD/CadQuery (Roadmap).

## E8 – Automatische Konsistenzprüfung statt automatischer Übernahme
- **Problem:** Positionen werden von Hand von `design.py` in die `.scad` übertragen.
- **Alternativen:** `.scad`-Include aus `design.py` generieren, oder prüfen.
- **Entscheidung:** prüfen (`check_consistency.py`). Kein Eingriff in den bewährten Gehäuse-Build, und die Prüfung deckt auch die Pi-Software-GPIOs ab.
