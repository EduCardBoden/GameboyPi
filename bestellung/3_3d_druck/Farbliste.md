# 3D-Druck: Dateien und Farben (GBX-Design)

Material PLA, Schichthöhe 0,2 mm, 3 Wände, 20 % Infill, keine Stützen nötig. Gesamt ca. 85 g.

| Datei | Farbe | Hinweis |
|---|---|---|
| `front.stl` | Schwarz (matt) | Vorderseite liegt auf dem Druckbett |
| `front_logo_silver.stl` | Silber (Silk) | gehört zu `front.stl` („Teil hinzufügen“) |
| `front_logo_purple.stl` | Lila (Silk) | gehört zu `front.stl` |
| `back.stl` | Schwarz (matt) | Rückseite liegt auf dem Druckbett |
| `back_logo_silver.stl` | Silber | gehört zu `back.stl` |
| `back_logo_purple.stl` | Lila | gehört zu `back.stl` |
| `ab.stl` | Lila | 2 Tasten |
| `dpad.stl`, `startselect.stl`, `knob.stl` | Silber oder Schwarz | |

**Mehrfarbdrucker (Bambu AMS / Prusa MMU):** Die Logo-Dateien liegen deckungsgleich zur Schale. In den Slicer zur Schale dazuladen („Als Teil hinzufügen“) und die Farbe zuweisen.

**Nur Einfarbdruck möglich:** Die Logo-Teile einzeln in Silber und Lila drucken und einkleben. Vorher in `mechanical/cad-source/gameboy_pi_case.scad` `inlay_clearance = 0.1` setzen und die STLs neu exportieren (VS-Code-Task „Nur STLs exportieren“).

Vorschau: `design_front.png`, `design_back.png`.
