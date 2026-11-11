"""GameboyPi – gemeinsame Bauteil- und Netzliste für Schaltplan- und Platinen-Generator.

Platinenkoordinaten in mm, Ursprung oben links, y nach unten (Blick von vorne, wie in KiCad).
"pos" ist die Mitte der nummerierten Pads; "side" ist F (vorne) oder B (hinten).
Pin-Schlüssel sind Strings, weil manche Footprints Pads wie "T"/"TN" haben.

Quellen der Modulmaße:
  Display MSP2401 (ohne Touch) – lcdwiki.com MSP2401_Size.pdf (77.18 x 42.72 mm, AA 48.96 x 36.72 mm)
  PowerBoost 1000C         – github.com/adafruit/Adafruit-PowerBoost-1000C (Eagle .brd, 36.07 x 22.86 mm)
  PAM8302                  – github.com/adafruit/Adafruit-PAM8302-Mono-Amplifier-PCB (24.13 x 15.24 mm)
  ADS1115 STEMMA QT        – github.com/adafruit/ADS1X15-Breakout-Board-PCBs (25.40 x 17.78 mm)
"""

BOARD_W, BOARD_H, BOARD_R = 78.0, 134.0, 3.0

PI_PINS = {
    1: "+3V3", 17: "+3V3",
    2: "+5V", 4: "+5V",
    6: "GND", 9: "GND", 14: "GND", 20: "GND", 25: "GND", 30: "GND", 34: "GND", 39: "GND",
    3: "I2C_SDA",       # GPIO2  – ADS1115
    5: "I2C_SCL",       # GPIO3
    7: "PWR_KEEP",      # GPIO4  – gpio-poweroff: high solange Linux läuft
    8: "UART_TX",       # GPIO14 – Debug-Konsole
    10: "UART_RX",      # GPIO15
    36: "PWR_SW_SENSE", # GPIO16 – gpio-shutdown: low = Schalter auf AUS
    38: "LBO_N",        # GPIO20 – Akku < 3.2 V (PowerBoost LBO)
    # Tasten (interne Pull-ups, gpio-key Overlay)
    29: "BTN_UP",       # GPIO5
    31: "BTN_DOWN",     # GPIO6
    35: "BTN_LEFT",     # GPIO19
    37: "BTN_RIGHT",    # GPIO26
    16: "BTN_A",        # GPIO23
    15: "BTN_B",        # GPIO22
    11: "BTN_START",    # GPIO17
    13: "BTN_SELECT",   # GPIO27
    # Display ILI9341 an SPI0
    19: "LCD_MOSI",     # GPIO10
    21: "LCD_MISO",     # GPIO9
    23: "LCD_SCK",      # GPIO11
    24: "LCD_CS",       # GPIO8 / CE0
    22: "LCD_DC",       # GPIO25
    18: "LCD_RST",      # GPIO24
    # Audio PWM (audremap pins_12_13)
    32: "AUD_PWM_L",    # GPIO12
    33: "AUD_PWM_R",    # GPIO13
}

BUTTONS = [
    # ref, net, label, pos
    ("SW1", "BTN_UP", "UP", (19.0, 78.5)),
    ("SW2", "BTN_DOWN", "DOWN", (19.0, 93.5)),
    ("SW3", "BTN_LEFT", "LEFT", (11.5, 86.0)),
    ("SW4", "BTN_RIGHT", "RIGHT", (26.5, 86.0)),
    ("SW5", "BTN_A", "A", (64.0, 80.0)),
    ("SW6", "BTN_B", "B", (51.0, 87.0)),
    ("SW7", "BTN_SELECT", "SELECT", (32.0, 108.0)),
    ("SW8", "BTN_START", "START", (46.0, 108.0)),
]

# Display-Modul (Lage auf der Platine, aus der Maßzeichnung abgeleitet)
LCD_ORIGIN = (0.4, 8.0)          # linke obere Ecke der Modulplatine
LCD_SIZE = (77.18, 42.72)
LCD_AA_CENTER = (0.4 + 43.44, 8.0 + 21.36)
LCD_SPACER = 4.0                  # Abstandshalter Modul <-> Trägerplatine (SD-Slot des Moduls ist 3.0 mm hoch)

PARTS = []

R_AX = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
C_DISC = "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm"
TP_FP = "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm"


def part(ref, lib_id, value, footprint, pins, pos=None, side="F", angle=0, group="misc"):
    PARTS.append(dict(ref=ref, lib_id=lib_id, value=value, footprint=footprint,
                      pins={str(k): v for k, v in pins.items()}, pos=pos, side=side, angle=angle, group=group))


# ---------------- Raspberry Pi ----------------
# Pi Zero 2 W liegt mit der Bauteilseite zur Platine auf der Rückseite (Buchsenleiste 2x20, 8.5 mm)
part("J1", "Connector:Raspberry_Pi_2_3", "Raspberry Pi Zero 2 W",
     "Module:Raspberry_Pi_Zero_Socketed_THT_FaceDown_MountingHoles", PI_PINS, side="B", group="pi")

# ---------------- Display ----------------
part("J2", "Connector_Generic:Conn_01x14", "LCD 2.4in ILI9341 SPI (MSP2401)",
     "Connector_PinHeader_2.54mm:PinHeader_1x14_P2.54mm_Vertical",
     {1: "+5V", 2: "GND", 3: "LCD_CS", 4: "LCD_RST", 5: "LCD_DC", 6: "LCD_MOSI",
      7: "LCD_SCK", 8: "+3V3", 9: "LCD_MISO"},
     pos=(LCD_ORIGIN[0] + 2.0, LCD_ORIGIN[1] + 4.85 + 6.5 * 2.54), group="lcd")

# ---------------- Stromversorgung ----------------
# PowerBoost 1000C, Stiftleiste JP2: 1 USB, 2 BAT, 3 VS, 4 EN, 5 GND, 6 LBO, 7 GND, 8 5V
part("J10", "Connector_Generic:Conn_01x08", "Adafruit PowerBoost 1000C",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
     {2: "VBAT", 4: "PB_EN", 5: "GND", 6: "PB_LBO", 7: "GND", 8: "+5V"},
     pos=(8.77, 112.28), side="B", angle=180, group="power")
# Ein/Aus: Stellung EIN zieht PWR_REQ auf GND, Stellung AUS meldet PWR_SW_SENSE an den Pi
part("SW9", "Switch:SW_SPDT", "POWER", "Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q",
     {1: "PWR_REQ", 2: "GND", 3: "PWR_SW_SENSE"}, pos=(60.0, 2.3), angle=180, group="power")
# Q1 zieht EN auf GND (= aus), sobald weder Schalter noch Pi (Q2) PWR_REQ auf GND halten
part("Q1", "Transistor_FET:BS170", "BS170", "Package_TO_SOT_THT:TO-92_Inline_Wide",
     {1: "PB_EN", 2: "PWR_REQ", 3: "GND"}, pos=(34.0, 114.0), side="B", group="power")
part("Q2", "Transistor_FET:BS170", "BS170", "Package_TO_SOT_THT:TO-92_Inline_Wide",
     {1: "PWR_REQ", 2: "PWR_KEEP", 3: "GND"}, pos=(41.5, 114.0), side="B", group="power")
part("R8", "Device:R", "1M", R_AX, {1: "VBAT", 2: "PWR_REQ"}, pos=(52.0, 114.0), side="B", group="power")
part("R9", "Device:R", "100k", R_AX, {1: "PWR_KEEP", 2: "GND"}, pos=(62.0, 114.0), side="B", group="power")
# LBO (bis 4.2 V) über Schottky-Diode auf 3.3-V-GPIO: nur nach unten ziehen
part("D2", "Device:D_Schottky", "BAT85", "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
     {1: "PB_LBO", 2: "LBO_N"}, pos=(36.0, 118.0), side="B", group="power")
# v1.2: 100k statt 10k. LBO des TPS61090 ist Open-Drain, max. 100 uA Low-Strom (TI-Datenblatt).
# 10k zogen ~0.3 mA. Mit 100k: (3.3 V - 0.25 V) / 100k = 31 uA. GPIO20-Pull im Pi ist aus (config.txt).
part("R10", "Device:R", "100k", R_AX, {1: "+3V3", 2: "LBO_N"}, pos=(46.0, 118.0), side="B", group="power")
# Akkuspannungsmessung: 100k/100k -> max. 2.1 V am ADS1115 AIN0
part("R11", "Device:R", "100k", R_AX, {1: "VBAT", 2: "VBAT_SENSE"}, pos=(56.0, 118.0), side="B", group="power")
part("R12", "Device:R", "100k", R_AX, {1: "VBAT_SENSE", 2: "GND"}, pos=(66.0, 118.0), side="B", group="power")
part("C6", "Device:C", "100nF", C_DISC, {1: "VBAT_SENSE", 2: "GND"}, pos=(55.0, 124.5), side="B", group="power")
part("C1", "Device:C_Polarized", "470uF 10V 10YXJ470M6.3X11", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
     {1: "+5V", 2: "GND"}, pos=(66.0, 126.0), side="B", group="power")
part("D1", "Device:LED", "LED rot 3mm", "LED_THT:LED_D3.0mm", {1: "GND", 2: "LED_A"}, pos=(12.5, 56.0), group="power")
part("R1", "Device:R", "1k", R_AX, {1: "+5V", 2: "LED_A"}, pos=(24.0, 60.0), group="power")

# ADS1115 STEMMA QT: JP2 = VCC GND SCL SDA ADDR ALERT, JP1 = AVDD AIN3 AIN2 AIN1 AIN0 AGND
part("J11", "Connector_Generic:Conn_01x06", "ADS1115 JP2 (VCC..ALERT)",
     "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
     {1: "+3V3", 2: "GND", 3: "I2C_SCL", 4: "I2C_SDA", 5: "GND"}, pos=(32.54, 84.7), side="B", angle=180, group="adc")
part("J12", "Connector_Generic:Conn_01x06", "ADS1115 JP1 (AVDD..AGND)",
     "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
     {5: "VBAT_SENSE", 6: "GND"}, pos=(45.24, 84.7), side="B", angle=180, group="adc")

# ---------------- Audio ----------------
# PWM-Filter wie beim Pi 3 (270R/150R/33nF), DC-Entkopplung 100uF für 32-Ohm-Kopfhörer
# Spalte bei x=15.5 vorne: hält Abstand zur PowerBoost-Stiftleiste (x=8.77, Durchsteckpads hinten)
AUD_RX = 15.2   # Widerstandsspalte
for ch, (r_ser, r_sh, y0) in {"L": ("R2", "R3", 113.0), "R": ("R4", "R5", 119.6)}.items():
    part(r_ser, "Device:R", "270", R_AX, {1: "AUD_PWM_" + ch, 2: "AUD_%s_F" % ch}, pos=(AUD_RX, y0), group="audio")
    part(r_sh, "Device:R", "150", R_AX, {1: "AUD_%s_F" % ch, 2: "GND"}, pos=(AUD_RX, y0 + 3.3), group="audio")
part("C2", "Device:C", "33nF", C_DISC, {1: "AUD_L_F", 2: "GND"}, pos=(23.5, 113.5), group="audio")
part("C4", "Device:C", "33nF", C_DISC, {1: "AUD_R_F", 2: "GND"}, pos=(23.5, 117.0), group="audio")
# Panasonic ECE-A1AKS101: 100 uF 10 V, Ø6.3 x 6 mm (niedrig genug für den 8.8-mm-Front-Hohlraum)
part("C3", "Device:C_Polarized", "100uF 10V ECE-A1AKS101", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
     {1: "AUD_L_F", 2: "HP_L"}, pos=(23.75, 122.0), group="audio")
part("C5", "Device:C_Polarized", "100uF 10V ECE-A1AKS101", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
     {1: "AUD_R_F", 2: "HP_R"}, pos=(23.75, 128.9), group="audio")
# Klinkenbuchse mit Schaltkontakten: ohne Stecker gehen T/R über TN/RN zum Lautsprecherpfad
part("J7", "Connector_Audio:AudioJack3_SwitchTR", "SJ1-3525N", "Connector_Audio:Jack_3.5mm_CUI_SJ1-3525N_Horizontal",
     {"T": "HP_L", "R": "HP_R", "S": "GND", "TN": "SPK_L", "RN": "SPK_R"}, pos=(34.0, 126.2), group="audio")
# v1.2: 47k statt 10k begrenzen die Lautsprecherleistung. PAM8302 hat 24 dB (x15.8) und schafft
# ~1.4 W an 8 Ohm, der AS02008MR-5-R verträgt 0.5 W (max. 0.8 W). Mit 47k bleibt AMP_IN bei
# Vollaussteuerung (0.42 V eff.) auch ohne Last unter 0.126 V eff. -> <= 2.0 V eff. = 0.5 W. Rechnung: PCB_DESIGN.md
part("R6", "Device:R", "47k", R_AX, {1: "SPK_L", 2: "SPK_MIX"}, pos=(AUD_RX, 126.2), group="audio")
part("R7", "Device:R", "47k", R_AX, {1: "SPK_R", 2: "SPK_MIX"}, pos=(AUD_RX, 129.5), group="audio")
# Lautstärke (Achse zeigt aus der linken Gehäuseseite)
# Bourns PTV09A-2020F-A103: liegend (PTV09A-2), 10k log, abgeflachte 6-mm-Achse (passt zum Knopf)
part("RV1", "Device:R_Potentiometer", "PTV09A-2020F-A103 10k log", "Potentiometer_THT:Potentiometer_Bourns_PTV09A-2_Single_Horizontal",
     {1: "GND", 2: "AMP_IN", 3: "SPK_MIX"}, pos=(5.35, 57.5), side="B", angle=0, group="audio")
# PAM8302 (Adafruit) JP1: 1 GND, 2 VIN, 3 SD, 4 A-, 5 A+
part("J3", "Connector_Generic:Conn_01x05", "Adafruit PAM8302",
     "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
     {1: "GND", 2: "+5V", 4: "GND", 5: "AMP_IN"}, pos=(68.0, 96.0), side="B", angle=270, group="audio")

# ---------------- Service ----------------
part("J8", "Connector_Generic:Conn_01x03", "UART Debug (GND TX RX)",
     "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     {1: "GND", 2: "UART_TX", 3: "UART_RX"}, pos=(46.54, 124.5), side="B", angle=270, group="service")
for i, net in enumerate(["VBAT", "+5V", "+3V3", "GND", "PB_EN", "AMP_IN"]):
    part("TP%d" % (i + 1), "Connector:TestPoint", net, TP_FP, {1: net}, pos=(44.0 + 5 * i, 131.5), side="B", group="service")

for ref, net, label, pos in BUTTONS:
    part(ref, "Switch:SW_Push", label, "Button_Switch_THT:SW_PUSH_6mm", {1: net, 2: "GND"}, pos=pos, group="buttons")

# ---------------- Mechanik ----------------
for i, (x, y) in enumerate([(4, 4), (74, 4), (4, 130), (74, 130)], 1):
    part("H%d" % i, "Mechanical:MountingHole", "M2.5", "MountingHole:MountingHole_2.7mm_M2.5", {}, pos=(x, y), group="mech")
part("H5", "Mechanical:MountingHole", "Kabel Lautsprecher", "MountingHole:MountingHole_3.2mm_M3", {}, pos=(73.0, 106.0), group="mech")
# Display-Abstandshalter (M3 x 4 mm) an den beiden Modullöchern gegenüber der Stiftleiste
for i, y in enumerate((LCD_ORIGIN[1] + 3.0, LCD_ORIGIN[1] + 39.72)):
    part("H%d" % (6 + i), "Mechanical:MountingHole", "M3 Display", "MountingHole:MountingHole_3.2mm_M3", {},
         pos=(LCD_ORIGIN[0] + 77.18 - 4.96, y), group="mech")

POWER_NETS = {"+5V": 1.0, "GND": 1.0, "+3V3": 0.5}
