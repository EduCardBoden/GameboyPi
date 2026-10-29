# Montageanleitung

## Werkzeug

- Lötkolben (temperaturgeregelt, 60 W, Bleistiftspitze + 2-mm-Meißelspitze für GND-Pins an Flächen), Lötzinn 0,5–0,8 mm, Flussmittel, Entlötlitze
- Seitenschneider, Abisolierzange, Pinzette
- Multimeter (Pflicht für die Inbetriebnahme)
- Kreuzschraubendreher PH0/PH1, Innensechskant/Schlüssel für M2,5/M3
- FDM-3D-Drucker (Bauraum ≥ 150 × 100 mm), Messschieber
- optional: USB-UART-Adapter (3,3 V), Labornetzteil mit Strombegrenzung, Heißkleber, Feile/Entgrater

## 1. Platine bestellen

`electronics/gerber/GameboyPi_Gerber.zip` hochladen, z. B. bei JLCPCB oder PCBWay. Einstellungen: 2 Lagen, 1,6 mm, 1 oz Kupfer, HASL. Alles andere bleibt Standard. Bestückung durch den Hersteller ist nicht nötig, alle Teile sind bedrahtet (THT). Die Pick-and-Place-Datei `electronics/assembly/GameboyPi_pick_and_place.csv` liegt trotzdem bei.

Bestückungspläne: `electronics/assembly/Bestueckung_vorne.pdf` und `Bestueckung_hinten.pdf` (gespiegelt).

## 2. Löten – Reihenfolge (flach → hoch)

**Vorderseite (F):**
1. Widerstände R1–R7, Kondensatoren C2, C4, Elkos C3/C5 (100 µF, **max. 7 mm hoch**, Polarität!)
2. LED D1: lange Beine lassen. Die LED-Spitze soll später im Loch der Front sitzen, Abstand Platine → Frontinnenseite ca. 8,8 mm.
3. Taster SW1–SW8, Schiebeschalter SW9 (Hebel ragt über die Oberkante), Klinke J7
4. Display noch **nicht**

**Rückseite (B):**
5. R8–R12, D2 (BAT85, Ring = Kathode zur Markierung „K“), C6, Q1/Q2 (flache Seite wie Aufdruck), C1 470 µF, Stiftleiste J8 (UART)
6. Poti RV1 (Achse zeigt nach links aus der Platine)
7. 2×20-**Buchsen**leiste für den Pi auf die Rückseite, von vorne löten
8. Module auf ihren Stiftleisten, jeweils Bauteilseite nach außen: PowerBoost (J10, Micro-USB zur Unterkante), PAM8302 (J3), ADS1115 (J11 + J12). Pinbelegung mit dem Aufdruck vergleichen.

## 3. Inbetriebnahme ohne Pi und Display

Siehe [testing.md](testing.md), Abschnitt „Inbetriebnahme“. Nur weitermachen, wenn TP2 = 5,0–5,3 V und keine Kurzschlüsse vorhanden sind.

## 4. Display

1. Zwei M3-×-4-mm-Abstandshülsen an H6/H7 (rechte Seite) mit M3-Schrauben durch Modul und Platine befestigen. Die Muttern kommen hinten hin.
2. Die Stiftleiste des Moduls durch J2 stecken, Modul plan auf die Hülsen legen und von hinten verlöten. Die Pins stehen ca. 2,8 mm über, kürzen.
3. Pin 1 (VCC) liegt oben, neben dem Aufdruck „VCC“.

## 5. Gehäuse drucken

| Teil | Datei | Ausrichtung | Hinweise |
|---|---|---|---|
| Vorderschale | `mechanical/stl/front.stl` | Front auf dem Bett | keine Stützen |
| Rückschale | `mechanical/stl/back.stl` | Rückwand auf dem Bett | Stützen nur für die Port-Öffnungen oben (optional) |
| D-Pad, A/B (2×), Start/Select (2×) | `dpad.stl`, `ab.stl`, `startselect.stl` | Kappe auf dem Bett | Flansch-Überhang 1,5 mm ist ohne Stütze druckbar |
| Lautstärkeknopf | `knob.stl` | flach | Bohrung ggf. mit 6-mm-Bohrer nacharbeiten |
| Logo-Einlagen | `front_logo_silver/purple.stl`, `back_logo_silver/purple.stl` | wie die zugehörige Schale | siehe „GBX-Design“ |

Einstellungen: PLA oder PETG, 0,2 mm Schicht, 3 Wände (≥ 1,2 mm), 20 % Infill. Für die Tasten 0,12 mm Schicht für glatte Oberflächen.

### GBX-Design (Farben und Logo)

| Bauteil | Farbe | Filament-Vorschlag |
|---|---|---|
| Vorder- und Rückschale | Schwarz | mattes Schwarz (PLA Matte) |
| „GB“ und Slogans (`*_logo_silver.stl`) | Chrom-Silber | Silk-PLA Silber |
| „X“ und Akzentlinie (`*_logo_purple.stl`) | Lila | Silk-PLA Lila/Violett |
| A/B-Tasten | Lila | wie oben |
| D-Pad, Start/Select, Lautstärkeknopf | Silber oder Schwarz | wie oben |

Das Logo ist 0,6 mm tief in die Außenfläche eingelassen (Vorderseite unter dem Display, Rückseite groß mit Slogans). Drei Möglichkeiten:

1. **Mehrfarbdrucker (Bambu AMS, Prusa MMU …):** `front.stl` laden, dann `front_logo_silver.stl` und `front_logo_purple.stl` per *„Teil hinzufügen“* bzw. *„Als Teil laden“* dazuladen. Die Dateien liegen bereits deckungsgleich. Den Teilen Silber und Lila zuweisen, mit der Rückschale genauso verfahren. Weil die Außenseite unten liegt, wechselt die Farbe nur in den ersten 3 Schichten.
2. **Einfarbdrucker, Einlagen:** In `gameboy_pi_case.scad` `inlay_clearance = 0.1` setzen, STLs neu exportieren, die Einlagen einzeln in Silber/Lila drucken (0,6 mm flach) und mit Sekundenkleber in die Vertiefungen kleben.
3. **Einfarbdrucker, Farbe:** Die Vertiefungen mit Lackstift (Silber/Lila) ausmalen und überstehende Farbe mit Isopropanol abwischen.

Druckqualität der Schrift: Die Slogans sind etwa 2,5 mm hoch, mit mindestens 0,45 mm Linienbreite. Mit 0,4-mm-Düse und erster Schicht 0,2 mm druckbar. Mit 0,2-mm-Düse werden sie noch schärfer.
Toleranzen: Tastenspiel 0,25 mm (`tol`), Schraublöcher 2,2 mm für M2,5 selbstschneidend.

## 6. Endmontage

1. Tasten von innen in die Vorderschale legen: D-Pad, A/B, Start/Select.
2. Lautsprecher in den Ring kleben (Heißkleber am Rand), Kabel durch H5 zur Rückseite und an die Schraubklemme des PAM8302.
3. 0,5-mm-Moosgummi rund um das Displayfenster innen aufkleben, optional die Acrylscheibe außen in die Vertiefung.
4. Platine einlegen: Display im Glasrahmen, LED im Loch, Schalterhebel im Schlitz, Klinke in der Öffnung.
5. Akku mit Kapton auf das markierte Feld in den Akkurahmen der Rückschale legen und den JST-Stecker in den PowerBoost stecken. **Vorher die Polarität prüfen:** Rot muss an + (Aufdruck am PowerBoost). Es gibt Akkus mit vertauschtem Stecker.
6. Raspberry Pi mit vorbereiteter SD-Karte aufstecken und mit 4 Abstandsbolzen M2,5 × 11 sichern.
7. Lautstärkeknopf auf die gekürzte Poti-Achse stecken (erst nach dem Schließen, er sitzt außen).
8. Rückschale aufsetzen, 4 × M2,5 × 20 von hinten einschrauben, nicht zu fest.

## 7. Software

Siehe [../software/setup-guide.md](../software/setup-guide.md).
