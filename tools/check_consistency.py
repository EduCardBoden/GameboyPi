"""GameboyPi Konsistenzprüfung: design.py <-> Gehäuse (.scad) <-> Pi-Software.

Prüft automatisch, was bisher von Hand übertragen wurde:
  1. Bauteilpositionen in gameboy_pi_case.scad ("Bauteil-Positionen (aus design.py)")
  2. GPIO-Nummern in config.txt.append, install.sh und battery_monitor.py gegen PI_PINS

Nur Standardbibliothek, läuft mit jedem Python >= 3.8. Aufruf aus der Repo-Wurzel:
    python tools/check_consistency.py
Exit-Code 0 = alles konsistent, 1 = Abweichung.
"""
import ast
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 0.01  # mm

# 40-polige Pi-Leiste: physischer Pin -> BCM-GPIO (nur Signalpins)
PIN_TO_BCM = {3: 2, 5: 3, 7: 4, 8: 14, 10: 15, 11: 17, 12: 18, 13: 27, 15: 22, 16: 23, 18: 24,
              19: 10, 21: 9, 22: 25, 23: 11, 24: 8, 26: 7, 27: 0, 28: 1, 29: 5, 31: 6, 32: 12,
              33: 13, 35: 19, 36: 16, 37: 26, 38: 20, 40: 21}

errors = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def load_design():
    path = os.path.join(ROOT, "electronics", "kicad-project", "design.py")
    spec = importlib.util.spec_from_file_location("design", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def scad_value(src, name):
    """Liest 'name = <Zahl | [Zahl, Zahl] | [[..],[..]]>;' aus der .scad-Datei."""
    m = re.search(r"^\s*%s\s*=\s*([^;]+);" % re.escape(name), src, re.M)
    if not m:
        raise KeyError(name)
    expr = m.group(1).split("//")[0].strip()
    return ast.literal_eval(expr)  # nur Zahlen und Listen, kein Code


def near(a, b):
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(near(x, y) for x, y in zip(a, b))
    return abs(a - b) <= TOL


def main():
    d = load_design()
    parts = {p["ref"]: p for p in d.PARTS}
    scad = read("mechanical", "cad-source", "gameboy_pi_case.scad")

    # ---- 1. Mechanik ----
    holes = [list(parts["H%d" % i]["pos"]) for i in range(1, 5)]
    check(near(scad_value(scad, "holes"), holes), "Montagelöcher H1-H4 weichen ab: scad %s, design %s"
          % (scad_value(scad, "holes"), holes))
    btn = {b[1]: b[3] for b in d.BUTTONS}
    dpad_c = [(btn["BTN_LEFT"][0] + btn["BTN_RIGHT"][0]) / 2, (btn["BTN_UP"][1] + btn["BTN_DOWN"][1]) / 2]
    for var, want in [("dpad_c", dpad_c), ("btn_a", btn["BTN_A"]), ("btn_b", btn["BTN_B"]),
                      ("btn_sel", btn["BTN_SELECT"]), ("btn_sta", btn["BTN_START"]),
                      ("led", parts["D1"]["pos"]), ("lcd_org", d.LCD_ORIGIN), ("lcd_mod", d.LCD_SIZE)]:
        got = scad_value(scad, var)
        check(near(got, list(want)), "%s: scad %s, design.py %s" % (var, got, list(want)))
    check(near(scad_value(scad, "jack_x"), parts["J7"]["pos"][0]), "jack_x passt nicht zu J7")
    check(near(scad_value(scad, "vol_y"), parts["RV1"]["pos"][1]), "vol_y passt nicht zu RV1")
    check(near(scad_value(scad, "pwr_sw")[0], parts["SW9"]["pos"][0]), "pwr_sw x passt nicht zu SW9")
    check(near(scad_value(scad, "lcd_spacer"), d.LCD_SPACER), "lcd_spacer weicht von LCD_SPACER ab")
    check(near([scad_value(scad, "pcb_w"), scad_value(scad, "pcb_h")], [d.BOARD_W, d.BOARD_H]),
          "Platinenmaße pcb_w/pcb_h weichen von BOARD_W/BOARD_H ab")
    # D-Pad-Taster liegen 7.5 mm um die Mitte (dpad() sw_off)
    for net in ("BTN_UP", "BTN_DOWN", "BTN_LEFT", "BTN_RIGHT"):
        dist = ((btn[net][0] - dpad_c[0]) ** 2 + (btn[net][1] - dpad_c[1]) ** 2) ** 0.5
        check(near(dist, 7.5), "%s liegt %.2f mm statt 7.5 mm von der D-Pad-Mitte" % (net, dist))

    # ---- 2. GPIO ----
    gpio = {net: PIN_TO_BCM[pin] for pin, net in d.PI_PINS.items() if pin in PIN_TO_BCM}
    cfg = read("software", "configuration", "config.txt.append")
    keys = {lbl: int(g) for g, lbl in re.findall(r"gpio-key,gpio=(\d+),keycode=\d+,label=\"(\w+)\"", cfg)}
    for lbl in ("UP", "DOWN", "LEFT", "RIGHT", "A", "B", "START", "SELECT"):
        check(keys.get(lbl) == gpio["BTN_" + lbl], "Taste %s: config.txt GPIO%s, Platine GPIO%s"
              % (lbl, keys.get(lbl), gpio["BTN_" + lbl]))
    m = re.search(r"gpio-shutdown,gpio_pin=(\d+)", cfg)
    check(m and int(m.group(1)) == gpio["PWR_SW_SENSE"], "gpio-shutdown-Pin passt nicht zu PWR_SW_SENSE")
    m = re.search(r"gpio-poweroff,gpiopin=(\d+)", cfg)
    check(m and int(m.group(1)) == gpio["PWR_KEEP"], "gpio-poweroff-Pin passt nicht zu PWR_KEEP")
    check("audremap,pins_%d_%d" % (gpio["AUD_PWM_L"], gpio["AUD_PWM_R"]) in cfg, "audremap-Pins passen nicht")
    check(re.search(r"^gpio=%d=ip,pn" % gpio["LBO_N"], cfg, re.M) is not None, "LBO-GPIO ohne Pull fehlt")
    inst = read("software", "configuration", "install.sh")
    check("GPIO_TFT_DATA_CONTROL=%d" % gpio["LCD_DC"] in inst, "fbcp DC-Pin passt nicht zu LCD_DC")
    check("GPIO_TFT_RESET_PIN=%d" % gpio["LCD_RST"] in inst, "fbcp RST-Pin passt nicht zu LCD_RST")
    check(gpio["LCD_CS"] == 8 and gpio["LCD_SCK"] == 11 and gpio["LCD_MOSI"] == 10,
          "Display nicht an SPI0 (fbcp-ili9341 erwartet CE0/SCLK/MOSI = GPIO8/11/10)")
    bm = read("software", "configuration", "battery_monitor.py")
    m = re.search(r"^LBO_GPIO\s*=\s*(\d+)", bm, re.M)
    check(m and int(m.group(1)) == gpio["LBO_N"], "battery_monitor LBO_GPIO passt nicht zu LBO_N")
    check(gpio["I2C_SDA"] == 2 and gpio["I2C_SCL"] == 3, "ADS1115 nicht an I2C1 (GPIO2/3)")
    # keine Doppelbelegung
    used = [g for g in gpio.values()]
    check(len(used) == len(set(used)), "GPIO doppelt belegt")

    print("Konsistenzprüfung: %d Prüfungen, %d Abweichung(en)" % (checks, len(errors)))
    for e in errors:
        print("  FEHLER:", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
