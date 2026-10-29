# Einkaufsliste GameboyPi (für 1 Gerät, Lieferung nach Wien)

Alle Teile sind **bedrahtet oder Module mit Stiftleisten**, also gut von Hand lötbar. Die Footprints auf der Platine passen genau zu diesen Bestellnummern.
Preise sind **Schätzungen** (Herbst 2026). Prüf vor dem Bestellen Preis und Lagerbestand.

## A) Ein Warenkorb bei DigiKey oder Mouser (liefern beide nach Österreich)

Die Datei **`digikey_mouser_bom.csv`** enthält alle Teile mit Herstellernummer und Menge (mit etwas Reserve):

- **DigiKey:** digikey.at → *BOM Manager* bzw. *„Liste hochladen“* → CSV hochladen → alle in den Warenkorb.
- **Mouser:** mouser.at → *BOM Tool* → CSV hochladen.

Ist ein Teil nicht lagernd, schlägt der Shop Alternativen vor. Achte dabei auf **gleiche Bauform und gleiches Rastermaß**, besonders beim Schiebeschalter, der Klinke und dem Poti.

| Teil | Herstellernr. | Menge | ca. € |
|---|---|---|---|
| Adafruit PowerBoost 1000C | 2465 | 1 | 20 |
| Adafruit PAM8302 Verstärker | 2130 | 1 | 4 |
| Adafruit ADS1115 (STEMMA-QT-Version!) | 1085 | 1 | 14 |
| Schiebeschalter abgewinkelt | C&K OS102011MA1QN1 | 1 | 0,70 |
| Klinkenbuchse 3,5 mm mit Schaltkontakten | Same Sky SJ1-3525N | 1 | 1,50 |
| Poti 10 kΩ log, liegend, abgeflachte Achse | Bourns PTV09A-2020F-A103 | 1 | 1,50 |
| Taster 6 × 6 × 5 mm | Omron B3F-1020 | 10 | 2,50 |
| MOSFET | onsemi BS170 | 3 | 1 |
| Schottky-Diode | Vishay BAT85 | 2 | 0,30 |
| Lautsprecher 20 mm, 8 Ω | PUI Audio AS02008MR-5-R | 1 | 3 |
| Buchsenleiste 2 × 20, 8,5 mm hoch (für den Pi) | Sullins PPTC202LFBN-RC | 1 | 2 |
| Stiftleiste 1 × 3 (UART) | Sullins PRPC003SAAN-RC | 1 | 0,30 |
| Widerstände 0,25 W (1k, 270R, 150R, 10k, 1M, 100k) | Yageo MFR-25FBF52-… | siehe CSV | 2 |
| Keramikkondensatoren 33 nF / 100 nF, RM 2,5 | Vishay K333K15X7RF5TL2 / K104K15X7RF5TL2 | 3 / 2 | 1 |
| **Zwischensumme** | | | **≈ 54 €** + Versand (ab ca. 50 € oft gratis) |

**Ebenfalls in der CSV (seit v1.1b):** Elkos C3/C5 Panasonic **ECE-A1AKS101** (100 µF 10 V, Ø 6,3 × 6 mm), C1 Rubycon **10YXJ470M6.3X11** (470 µF 10 V), LED Lite-On **LTL-4221N** (rot, 3 mm).

## B) Raspberry Pi, Display, Akku

| Teil | Wo | ca. € | Hinweise |
|---|---|---|---|
| **Raspberry Pi Zero 2 WH** (mit angelöteter Stiftleiste) | BerryBase, Welectron, Mouser/DigiKey | 20 | Die „WH“-Version spart das Löten der Pi-Stiftleiste. |
| **microSD 32 GB** | Amazon (im Warenkorb): Verbatim Premium 32 GB | 12 | |
| **Display LAFVIN 2,4" SPI ILI9341 (mit Touch, entspricht MSP2402)** | Amazon (im Warenkorb) | 16 | Laut Produktbild Platine **77,18 × 42,72 mm**, Anzeigefläche 36,72 × 48,96 mm, gleiche 14-polige Belegung. Das Gehäuse ist für die Touch-Dicke ausgelegt (`lcd_touch = 1.3`). |
| **LiPo-Akku 103450**, 3,7 V, 2000 mAh, **mit Schutzschaltung**, Stecker **JST 2,0 mm** | Amazon (im Warenkorb): 2er-Set | 13 | Maße max. **52 × 35 × 10 mm** (Rahmen im Gehäuse 53 × 35). **Polarität vor dem Einstecken messen.** Rot muss an „+“ am PowerBoost, manche Akkus sind vertauscht. |

## C) Schrauben und Kleinmaterial (bei Amazon im Warenkorb)

| Teil | Produkt | ca. € |
|---|---|---|
| Pi-Abstandsbolzen M2,5 × 11 mm + Schrauben/Muttern | GeeekPi 220-tlg. M2,5-Set | 12,10 |
| Gehäuseschrauben M2,5 × 20 (4 nötig) | Kozelo 30 Stk. Zylinderkopf, Edelstahl | 4,63 |
| Display: 2 × Schraube M3 × 14 + 2 × Mutter M3 | Ewwtrey 260-tlg. M3-Nylon-Set | 7,04 |
| Display-Abstandshülsen 4 mm (2) | **mitdrucken**: `spacers.stl` | – |
| Litze 0,14 mm² (Lautsprecher), Kapton-Band, Moosgummi 0,5 mm, doppelseitiges Klebeband | noch nicht im Warenkorb | ~5 |

## D) Werkzeug (falls noch nicht vorhanden)

Lötstation (temperaturgeregelt), Lötzinn 0,5–0,8 mm mit Flussmittel, Entlötlitze, Seitenschneider, Multimeter, Pinzette. Ein Einsteiger-Set gibt es ab ca. 30–50 €. Im **Happylab Wien** stehen Lötstationen zur Verfügung.

## Gesamtkosten (Schätzung)

| Block | ca. € |
|---|---|
| A) DigiKey/Mouser inkl. Elkos/LED | 55 |
| B) Pi, SD, Display, Akku | 45 |
| C) Schrauben, Kleinmaterial | 10 |
| Platinen (JLCPCB, 5 Stück) | 20–45 |
| 3D-Druck (je nach Weg) | 15–35 |
| **Summe** | **≈ 145–190 €** (ohne Werkzeug) |
