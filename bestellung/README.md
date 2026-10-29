# Bestellpaket GameboyPi

Alles, was du zum Bestellen brauchst, in drei Schritten:

| Schritt | Ordner | Was tun | ca. € |
|---|---|---|---|
| 1 | `1_platine_JLCPCB/` | `GameboyPi_Gerber.zip` bei jlcpcb.com hochladen, Einstellungen laut `JLCPCB_Bestellung.md` | 20–45 |
| 2 | `2_bauteile/` | `digikey_mouser_bom.csv` bei DigiKey oder Mouser hochladen; Pi, Display, Akku laut `Einkaufsliste.md` | 110 |
| 3 | `3_3d_druck/` | STLs + `Farbliste.md` an den Drucker (willhaben / Happylab / Hubs) | 15–35 |

Danach: löten nach `documentation/assembly-guide.md`, vor dem Einschalten den Messplan in `documentation/testing.md` abarbeiten, Software nach `software/setup-guide.md`.

**Tipp zur Reihenfolge:** Zuerst die Platinen bestellen, die brauchen am längsten (1–3 Wochen). Bauteile und 3D-Druck kommen meist innerhalb weniger Tage.
