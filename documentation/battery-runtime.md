# Stromverbrauch und Akkulaufzeit

Alle Werte sind **Abschätzungen** aus Herstellerangaben und typischen Messwerten der Community. Gemessen wurde am realen Gerät noch nichts, es wurde noch nicht gebaut.

## Verbraucher (am 5-V-Ausgang des PowerBoost)

| Verbraucher | typisch | Spitze | Quelle / Annahme |
|---|---|---|---|
| Raspberry Pi Zero 2 W, Emulation (1 Kern hoch belastet, WLAN an) | 350 mA | 600 mA | übliche Messwerte; Raspberry Pi gibt keinen festen Wert an |
| Display MSP2402 (Logik + Hintergrundlicht) | 115 mA | 115 mA | Datenblatt: 0,57 W Leistungsaufnahme → 0,57 W / 5 V |
| PAM8302 + 8-Ω-Lautsprecher, mittlere Lautstärke | 60 mA | 300 mA | Class-D, Spitzen bei lauten Passagen |
| ADS1115, LEDs, Pull-ups | 5 mA | 5 mA | |
| **Summe** | **≈ 530 mA (2,65 W)** | **≈ 1,0 A** | |

## Wandler und Akku

- PowerBoost 1000C: 5,2 V Ausgang. Nennwert 1 A, ab ~500 mA sinkt die Spannung laut Adafruit Richtung 5,0 V. Den Wirkungsgrad schätze ich mit **≈ 85 %**.
- Akku: LiPo 103450, nominal 3,7 V × 2000 mAh = **7,4 Wh**. Nutzbar bis zur LBO-Abschaltung (3,2 V) sind etwa **90 % ≈ 6,7 Wh**.

## Laufzeit

| Szenario | Last am Akku | Laufzeit |
|---|---|---|
| Game Boy / GBC / NES, WLAN aus, leise | 2,1 W / 0,85 ≈ 2,5 W | **≈ 2,7 h** |
| typisch (SNES, WLAN an, mittlere Lautstärke) | 2,65 W / 0,85 ≈ 3,1 W | **≈ 2,1 h** |
| Dauerlast (PS1, laut) | 3,8 W / 0,85 ≈ 4,5 W | **≈ 1,5 h** |

Rechnung: Laufzeit = 6,7 Wh / Last am Akku.

## Laden

- Ladestrom des PowerBoost 1000C: **1 A** (MCP73871). Bei 2000 mAh sind das 0,5 C, das liegt in der Standardladerate typischer 103450-Zellen. Bei Zellen unter 2000 mAh die erlaubte Laderate im Datenblatt prüfen.
- Ladezeit leer → voll: ca. **2,5 h**. Spielen während des Ladens geht, weil der PowerBoost Load-Sharing hat.
- Netzteil: 5 V / ≥ 2 A an Micro-USB. Mit Gerät an und gleichzeitigem Laden sind ~1,5 A möglich.

## Ströme, Schutz und Wärme

| Größe | Wert | Auslegung |
|---|---|---|
| max. Entladestrom Akku | ≈ 1,8 A (1 A × 5,2 V / 3,4 V / 0,85) | Zelle mit Schutzschaltung, typisch 1–2 C zulässig (2–4 A) ✔ |
| Tiefentlade-/Kurzschluss-/Überstromschutz | Schutzschaltung (PCM) im Akku + Abschaltung über LBO + Software | ✔ |
| 5-V-Leiterbahnen | 0,75–1,0 mm, 35 µm Cu (gemessen im Layout v1.2) | 1,9 A (0,75 mm) bzw. 2,4 A (1,0 mm) bei 10 K Erwärmung (IPC-2221, Außenlage) ✔ ≥ 1,9 × Spitzenlast |
| Header-Pin 5 V (PowerBoost → Platine) | 1 Pin, 2,54 mm | ≈ 3 A Nennstrom ✔ |
| Akkuleitung | vorkonfektioniert, ≥ 0,2 mm² (AWG 24) | ✔ für 1,8 A bei 5 cm Länge |
| Lautsprecherleitung | 0,14 mm² | ✔ |
| Wärme | Pi Zero 2 W unter Volllast ~1,5–2 W, PowerBoost ~0,5 W Verlust | Lüftungsschlitze über dem Pi. Den Akku nicht direkt über den Pi legen (ist er nicht, eigenes Feld). |
