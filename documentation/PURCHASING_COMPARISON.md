# Einkauf: Preis- und Lieferprüfung

**Abgerufen am 11.11.2026, ca. 19:55–20:10 Uhr MEZ**, Lieferung nach Österreich, Preise inkl. 20 % MwSt. Preise und Bestände ändern sich täglich, also vor der Bestellung neu prüfen. Es wurde **nichts bestellt**.

## Module (geprüft)

| Teil | Händler | Preis | Lieferstatus | Quelle |
|---|---|---|---|---|
| Pi Zero 2 WH | BerryBase.at (RPIZ-2WH) | 20,90 € | **nicht lieferbar** | berrybase.at/raspberry-pi-zero-2-wh |
| Pi Zero 2 W (ohne Stiftleiste) | BerryBase.at (RPIZ-2W) | 18,90 € | **nicht lieferbar**, max. 1 Stk./Kunde | berrybase.at/raspberry-pi-zero-2-w |
| Pi Zero 2 WH | Reichelt (SC0721) | 22,10 € | **widersprüchlich**: Shop-Suche „verfügbar ab 22.12.2026“, raspberry.tips (Stand 08.11.) „lieferbar, 1–2 Werktage“ | reichelt.com …-383360 |
| Pi Zero 2 W | Reichelt.at | 19,56 € | Shop-Suche: ab 22.12.2026 | reichelt.at …-313902 |
| PowerBoost 1000C | BerryBase.at (ADA2465) | 23,90 € | **nicht lieferbar** | berrybase.at/adafruit-powerboost-1000 |
| PowerBoost 1000C | Reichelt.at | 25,16 € | Bestand nicht abrufbar (Seite blockt Scraper) | Suchergebnis reichelt.at …-235493 |
| PowerBoost 1000C | Paradisetronic | 24,99 € | nicht geprüft | paradisetronic.com |
| PAM8302 | BerryBase.at (ADA2130) | 3,90 € | **nicht lieferbar** | berrybase.at/…-pam8302 |
| PAM8302 | Kiwi Electronics (NL) | 3,69 € netto (≈ 4,43 € inkl. 20 %) | 52 Stk. laut Suchergebnis | kiwi-electronics.com |
| PAM8302 | Botland (PL) | 5,50 € | nicht geprüft | botland.store |
| ADS1115 | BerryBase.at (ADA1085) | 15,90 € | **lieferbar, 61 Stk., 1–3 Tage** | berrybase.at/en/adafruit-ads1115… |

Hintergrund Pi-Knappheit (raspberry.tips, 08.11.2026): Engpass beim Chip-Substrat (Konkurrenz durch KI-Beschleuniger) und hohe Nachfrage. Raspberry Pi hat einen zweiten Substratlieferanten qualifiziert, Ware kommt in kleinen Mengen.

## Kleinteile (nicht neu geprüft)

Die DigiKey-Nummern in `digikey_mouser_bom.csv` stammen aus v1.1 (Okt. 2026), die Summe von ≈ 17–20 € ist eine Schätzung. Neu in v1.2: **Yageo MFR-25FBF52-47K** (DigiKey-Nr. 47.0KXBK-ND nach dem Muster der anderen Yageo-Nummern, beim Upload bestätigen). 10-kΩ-Widerstände entfallen.

## Empfohlener Einkaufsweg

| Schritt | Wo | Was | Begründung |
|---|---|---|---|
| 1 | **Reichelt** | Pi Zero 2 WH; falls lieferbar auch PowerBoost | Einziger Händler mit möglicher kurzfristiger Pi-Verfügbarkeit, EU-Versand |
| 2 | **DigiKey** (CSV-Upload) | alle Kleinteile + PAM8302 + PowerBoost (falls nicht bei Reichelt) | ein Warenkorb, Originalware, ein Versand. Mit den Modulen liegt der Warenkorb über ≈ 50 € (Versandschwelle laut v1.1, nicht neu geprüft) |
| 3 | **BerryBase.at** | ADS1115 (lieferbar) | oder ebenfalls über DigiKey (1528-1085-ND), wenn das den Versand spart |
| 4 | Amazon | Display LAFVIN, Akku 103450 (2er-Set), Schraubensets | wie v1.1 |
| 5 | JLCPCB | 5 Platinen | `bestellung/1_platine_JLCPCB/` |

**Fallback bei Pi-Mangel:** Pi Zero W (passt elektrisch und mechanisch, nur langsamer). Die Alternativen aus dem Artikel (Orange Pi Zero 2W, Radxa Zero 3W) haben andere Bauformen bzw. Treiber und passen **nicht** ohne Neukonstruktion.

## Gesamtkosten (Schätzung)

| Block | günstig | teuer | Basis |
|---|---|---|---|
| Pi Zero 2 WH | 22,10 | 22,10 | geprüft |
| microSD 32 GB | 7 | 12 | v1.1 |
| Display | 16 | 16 | v1.1 |
| Akku (½ 2er-Set bzw. Set) | 6,50 | 13 | v1.1 |
| PowerBoost | 23,90 | 25,16 | geprüft |
| PAM8302 | 3,90 | 5,50 | geprüft |
| ADS1115 | 15,90 | 15,90 | geprüft |
| Kleinteile DigiKey inkl. Lautsprecher | 17 | 20 | v1.1 |
| Schrauben/Kleinmaterial | 3 | 24 | anteilig bzw. ganze Sets |
| Platinen (5 Stk. inkl. Versand) | 20 | 45 | v1.1 (JLCPCB-Rechner nicht abgefragt) |
| 3D-Druck | 2 (eigener Drucker, 85 g) | 35 (Dienstleister) | 85 g aus STL berechnet |
| Versand der Händler | 10 | 25 | Schätzung |
| **Summe** | **≈ 147 €** | **≈ 259 €** | typisch ≈ 160–190 € |

Montage: Eigenleistung, geschätzt 4–6 h Löten und Zusammenbau, 1–2 h Software.
