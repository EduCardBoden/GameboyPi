# Montage-Checkliste (v1.2)

Kurzfassung zum Abhaken. Werkzeug, Lötreihenfolge und Fotos-Hinweise im Detail: [assembly-guide.md](assembly-guide.md). Messungen: [testing.md](testing.md) Teil B.

## Vorbereitung
- [ ] Platinen (5 Stk.) und alle Teile laut [FINAL_BOM.md](FINAL_BOM.md) da
- [ ] **ADS1115 ist die STEMMA-QT-Version** (zwei 6-polige Leisten, Pinfolge laut `wiring.md`)
- [ ] **Widerstandswerte v1.2:** R6/R7 = **47 kΩ** (gelb-violett-schwarz-rot-braun), R10 = **100 kΩ**
- [ ] Frontschale probedrucken und Taster, Klinke, Display einlegen, bevor alles gedruckt wird

## Löten
1. [ ] Vorderseite: R1–R7, C2, C4, C3/C5 (Polarität!), D1 (Polarität!), SW1–SW9, J7
2. [ ] Rückseite: R8–R12, D2 (Ring = Kathode zu PB_LBO), Q1/Q2 (flache Seite laut Druck), C6, C1, RV1, J8, 2×20-Buchse J1
3. [ ] Modul-Stiftleisten: PowerBoost J10, PAM8302 J3, ADS1115 J11/J12 (Module noch nicht aufsetzen)
4. [ ] Durchgesteckte Beinchen im Akkubereich bündig kürzen, Kapton darüber

## Inbetriebnahme ohne Pi (testing.md 1–3)
5. [ ] Widerstände TP2/TP3/TP1 gegen TP4 messen
6. [ ] PowerBoost aufsetzen, Akku-Polarität am JST messen, Akku anstecken
7. [ ] Schalter AUS → TP5 < 0,4 V, TP2 ≈ 0 V; EIN → TP2 = 5,0–5,3 V, LED an
8. [ ] Abschaltlogik mit externer 3,3 V an J1 Pin 7 prüfen

## Endmontage
9. [ ] Display auf 2 × 4-mm-Hülsen (M3 × 14), Stiftleiste J2 löten
10. [ ] PAM8302 + Lautsprecherkabel durch H5, ADS1115 aufsetzen
11. [ ] Tasten, Lautsprecher (Halter Ø 20,6), Moosgummi vor das Display, Platine in die Frontschale
12. [ ] Akku in den Rahmen der Rückschale, Pi aufstecken, Rückschale mit 4 × M2,5 × 20 verschrauben (handfest, PLA)
13. [ ] Poti-Achse auf ≈ 4 mm kürzen, Knopf aufstecken

## Software
14. [ ] RetroPie 4.8 flashen, `software/configuration/` kopieren, `sudo bash install.sh`
15. [ ] testing.md Teil 4 abarbeiten, `VBAT_CAL` abgleichen
