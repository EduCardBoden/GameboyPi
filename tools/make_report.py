"""Erzeugt documentation/final-report/GameBoy_Project_Engineering_Documentation.docx.

Benötigt python-docx (pip install python-docx). Optional: Pfad zu einer Bibliothek als 1. Argument.
Das Inhaltsverzeichnis ist ein Word-Feld: Word aktualisiert es beim Öffnen (F9) bzw. per
tools/finalize_report.ps1, das außerdem ein PDF zur Kontrolle erzeugt.
Alle Zahlen stammen aus documentation/*.md und project-log/ (Stand 11.11.2026).
"""
import os
import sys

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "documentation", "final-report")
OUT = os.path.join(OUT_DIR, "GameBoy_Project_Engineering_Documentation.docx")
PURPLE = RGBColor(0x4B, 0x2C, 0x82)
GREY = RGBColor(0x55, 0x55, 0x55)
FONT = "Calibri"

doc = Document()
fig_no = [0]
tab_no = [0]

# ---------------- Stile ----------------
st = doc.styles
st["Normal"].font.name = FONT
st["Normal"].font.size = Pt(10.5)
st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st["Normal"].paragraph_format.space_after = Pt(6)
st["Normal"].paragraph_format.line_spacing = 1.15
for name, size, before, after in (("Heading 1", 17, 18, 8), ("Heading 2", 13, 12, 4), ("Heading 3", 11.5, 8, 3)):
    s = st[name]
    s.font.name = FONT
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = PURPLE
    s.paragraph_format.space_before = Pt(before)
    s.paragraph_format.space_after = Pt(after)
    s.paragraph_format.keep_with_next = True
    rpr = s.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts"); rpr.append(fonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if fonts.get(qn(a)) is not None:
            del fonts.attrib[qn(a)]
cap = st["Caption"]
cap.font.name = FONT; cap.font.size = Pt(9); cap.font.italic = True; cap.font.color.rgb = GREY; cap.font.bold = False

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.3)
sec.top_margin, sec.bottom_margin = Cm(2.3), Cm(2.0)
CONTENT_W = 21.0 - 4.6


# ---------------- Hilfsfunktionen ----------------
def field(paragraph, instr):
    r = paragraph.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin"); r._r.append(b)
    t = OxmlElement("w:instrText"); t.set(qn("xml:space"), "preserve"); t.text = instr; r._r.append(t)
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate"); r._r.append(s)
    r2 = paragraph.add_run("1" if "PAGE" in instr else "Inhaltsverzeichnis wird in Word aktualisiert (F9).")
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    r3 = paragraph.add_run(); r3._r.append(e)
    return r2


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hex_color)
    tcPr.append(sh)


def bottom_border(paragraph, color="4B2C82", size=12):
    pPr = paragraph._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", str(size)), ("w:space", "4"), ("w:color", color)):
        b.set(qn(k), v)
    bdr.append(b); pPr.append(bdr)


def H1(t):
    doc.add_heading(t, level=1)


def H2(t):
    doc.add_heading(t, level=2)


def H3(t):
    doc.add_heading(t, level=3)


def P(text, bold_prefix=None, italic=False):
    p = doc.add_paragraph()
    if bold_prefix:
        p.add_run(bold_prefix).bold = True
    r = p.add_run(text); r.italic = italic
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def BUL(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        if isinstance(it, tuple):
            p.add_run(it[0]).bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)
        p.paragraph_format.space_after = Pt(2)


def TABLE(header, rows, widths, caption=None, font=9):
    if caption:
        tab_no[0] += 1
        c = doc.add_paragraph("Tabelle %d: %s" % (tab_no[0], caption), style="Caption")
        c.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    total = sum(widths)
    ws = [Cm(CONTENT_W * w / total) for w in widths]
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(font); r.font.color.rgb = RGBColor(255, 255, 255)
        shade(cell, "4B2C82")
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            para = cells[i].paragraphs[0]
            # **fett** auch innerhalb eines Zellentexts
            for k, part in enumerate(str(v).split("**")):
                if part:
                    rr = para.add_run(part); rr.bold = (k % 2 == 1); rr.font.size = Pt(font)
            if ri % 2 == 1:
                shade(cells[i], "F1EDF8")
    for row in t.rows:
        for i, c in enumerate(row.cells):
            c.width = ws[i]
            for para in c.paragraphs:
                para.paragraph_format.space_after = Pt(1)
                para.paragraph_format.line_spacing = 1.0
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def IMG(path, width_cm, caption):
    full = os.path.join(ROOT, path)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(full, width=Cm(width_cm))
    fig_no[0] += 1
    c = doc.add_paragraph("Abbildung %d: %s" % (fig_no[0], caption), style="Caption")
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER


def IMG2(path_a, path_b, width_cm, caption):
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, pth in zip(t.rows[0].cells, (path_a, path_b)):
        para = cell.paragraphs[0]; para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.add_run().add_picture(os.path.join(ROOT, pth), width=Cm(width_cm))
    fig_no[0] += 1
    c = doc.add_paragraph("Abbildung %d: %s" % (fig_no[0], caption), style="Caption")
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER


def NOTE(text, label="Hinweis: "):
    t = doc.add_table(rows=1, cols=1)
    cell = t.rows[0].cells[0]
    shade(cell, "F1EDF8")
    para = cell.paragraphs[0]
    para.add_run(label).bold = True
    para.add_run(text)
    for r in para.runs:
        r.font.size = Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ---------------- Deckblatt ----------------
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); r = p.add_run("GameboyPi v1.2"); r.font.size = Pt(34); r.bold = True; r.font.color.rgb = PURPLE
p = doc.add_paragraph(); r = p.add_run("Game-Boy-Projekt: Handheld-Spielkonsole auf Basis des Raspberry Pi Zero 2 W")
r.font.size = Pt(15); r.font.color.rgb = GREY
bottom_border(p)
p = doc.add_paragraph(); r = p.add_run("Technische Projektdokumentation – Elektronik, Leiterplatte, Gehäuse, Software, Beschaffung und Prüfung")
r.font.size = Pt(12)
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(os.path.join(ROOT, "mechanical/previews/design_front.png"), width=Cm(7.2))
c = doc.add_paragraph("Gehäuse-Vorderseite im GBX-Design (OpenSCAD-Rendering, kein Foto)", style="Caption")
c.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph()
TABLE(["Angabe", "Wert"], [
    ["Dokumentstand", "11. November 2026, Revision 1.2"],
    ["Projektstatus", "Entwurf vollständig und rechnerisch geprüft; nicht gebaut, nicht gemessen"],
    ["Quelldaten", "Git-Branch engineering-v1.2 (Basis-Tag baseline-v1.1)"],
], [1, 3])
page_break()

# ---------------- Inhaltsverzeichnis ----------------
p = doc.add_paragraph(); r = p.add_run("Inhaltsverzeichnis"); r.bold = True; r.font.size = Pt(17); r.font.color.rgb = PURPLE
field(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u')
page_break()

# ---------------- Kopf- und Fußzeile ----------------
hdr = sec.header.paragraphs[0]
hdr.text = "GameboyPi v1.2 – Technische Projektdokumentation"
hdr.runs[0].font.size = Pt(8.5); hdr.runs[0].font.color.rgb = GREY
bottom_border(hdr, "BBBBBB", 4)
sec.different_first_page_header_footer = True
st["Footer"].font.size = Pt(8.5)   # gilt auch für die von Word aktualisierten Feldergebnisse
ftr = sec.footer.paragraphs[0]; ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
rr = ftr.add_run("Seite "); rr.font.size = Pt(8.5)
field(ftr, "PAGE").font.size = Pt(8.5)
rr = ftr.add_run(" von "); rr.font.size = Pt(8.5)
field(ftr, "NUMPAGES").font.size = Pt(8.5)

# =====================================================================
H1("1 Projektübersicht")
H2("1.1 Zielsetzung")
P("Ziel des Projekts ist ein tragbares Retro-Spielgerät im Formfaktor des Game Boy Color, das klassische Konsolen "
  "(Game Boy, GBC, NES, SNES, PlayStation 1) emuliert. Herzstück ist ein Raspberry Pi Zero 2 W auf einer eigens "
  "entwickelten Trägerplatine. Ein 3D-gedrucktes Gehäuse nimmt Platine, Display, Akku und Bedienelemente auf. "
  "Das Gerät soll ausschließlich aus handlötbaren Bauteilen und fertigen Modulen bestehen, damit es ohne "
  "SMD-Bestückung beim Hersteller nachgebaut werden kann.")
H2("1.2 Ursprüngliches Konzept")
P("Das Konzept folgt dem Aufbau des Originals: Display oben, Steuerkreuz links, A/B rechts, Start/Select mittig, "
  "Lautsprecher unten rechts, Ein/Aus-Schalter an der Oberkante. Die Elektronik ist als „Generator-Projekt“ angelegt: "
  "Eine einzige Python-Datei (design.py) beschreibt alle Bauteile, Verbindungen und Positionen. Daraus entstehen "
  "Schaltplan und Leiterplatte automatisch. Das Gehäuse ist eine parametrische OpenSCAD-Datei.")
H2("1.3 Funktionsumfang")
TABLE(["Funktion", "Umsetzung"], [
    ["Rechner", "Raspberry Pi Zero 2 W (4 × Cortex-A53, 1 GHz, 512 MB), kompatibel mit Zero W"],
    ["Anzeige", "2,4\"-TFT ILI9341 SPI, 320 × 240, 60 Bilder/s mit fbcp-ili9341"],
    ["Bedienung", "D-Pad, A, B, Start, Select, Ein/Aus-Schiebeschalter, Lautstärkeregler"],
    ["Audio", "PWM-Stereo → Kopfhörerbuchse; Mono-Verstärker PAM8302 → 20-mm-Lautsprecher"],
    ["Energie", "LiPo 2000 mAh, Laden über Micro-USB, Spielen während des Ladens, sicheres Herunterfahren"],
    ["Akkuüberwachung", "16-Bit-ADC ADS1115 + Unterspannungssignal, automatische Abschaltung"],
    ["Service", "microSD seitlich, Mini-HDMI und USB oben, UART-Konsole, 6 Testpunkte"],
], [1, 3], "Funktionsumfang")
H2("1.4 Technische Ziele")
BUL(["Laufzeit ≥ 2 h bei typischer Nutzung",
     "Kein Datenverlust beim Ausschalten (Software-gesteuertes Abschalten statt hartem Trennen)",
     "Alle elektrischen Grenzwerte der Module eingehalten (Datenblattnachweis)",
     "Fertigbar mit Standardregeln eines günstigen Leiterplattenherstellers (JLCPCB)",
     "Gehäuse ohne Stützstrukturen auf einem FDM-Drucker druckbar",
     "Vollständige, nachvollziehbare und reproduzierbare Dokumentation"])

# =====================================================================
H1("2 Ausgangssituation")
H2("2.1 Vorhandene Hardware- und Software-Basis")
P("Zu Beginn dieses Entwicklungsabschnitts (11.11.2026) lag Version 1.1 vor: ein vollständiger, automatisch erzeugter "
  "KiCad-10-Entwurf mit Gerber-Daten, ein parametrisches Gehäuse mit 11 druckfertigen STL-Dateien, ein Bestellpaket "
  "sowie eine Pi-Konfiguration (Boot-Overlays, Installationsskript, Akku-Dienst). Physisch gebaut war nichts.")
TABLE(["Bereich", "Stand v1.1", "Werkzeug"], [
    ["Elektronik", "design.py → Schaltplan → Platine → Autorouting → Gerber", "KiCad 10.0.6, Freerouting 2.5"],
    ["Gehäuse", "gameboy_pi_case.scad, Kollisionsprüfung 21 Hüllkörper", "OpenSCAD 2021.01"],
    ["Software", "config.txt-Ergänzung, install.sh, battery_monitor.py", "RetroPie 4.8 (Buster)"],
    ["Prüfungen", "Netzliste, ERC, DRC, Kollision", "kicad-cli, OpenSCAD"],
], [1.1, 2.6, 1.4], "Ausgangsstand v1.1")
H2("2.2 Architektur v1.1")
P("Die Architektur ist modular: Der Pi sitzt kopfüber auf der Rückseite der Trägerplatine, das Display auf "
  "Abstandshaltern auf der Vorderseite. Die Stromversorgung übernimmt ein Adafruit PowerBoost 1000C, die "
  "Ein/Aus-Logik zwei MOSFETs. Hinweis zur Aufgabenstellung: Das Projekt enthält keinen AVR- oder "
  "Arduino-Mikrocontroller. Die „Firmware“ besteht aus Linux-Konfiguration, einem Display-Treiber und einem "
  "Python-Dienst. Die Prüfung der Embedded-Software wurde entsprechend auf diese Bausteine übertragen.")
H2("2.3 Ausgangsprobleme")
P("Die Bestandsaufnahme ergab neben den in der README dokumentierten Risiken folgende offene Punkte:")
BUL([("Unbelegte Annahmen: ", "Wert des EN-Pull-ups im PowerBoost unbekannt; Schaltschwelle der BS170 kritisch eingeschätzt."),
     ("Fehlende Grenzwertprüfung: ", "Ausgangsleistung des Verstärkers gegen die Belastbarkeit des Lautsprechers, Strom in den LBO-Ausgang."),
     ("Messfehler: ", "Belastung des Spannungsteilers durch den ADC-Eingang nicht berücksichtigt."),
     ("Doku-Abweichung: ", "5-V-Leiterbahnen als durchgehend 1,0 mm beschrieben, tatsächlich teils 0,75 mm."),
     ("Handübertrag: ", "Bauteilpositionen werden von Hand von der Platine ins Gehäuse übertragen, ohne automatische Kontrolle."),
     ("Software: ", "Akku-Dienst ohne Tests, Unterspannungssignal ohne Entprellung.")])

# =====================================================================
H1("3 Entwicklungsprozess")
P("Der Entwicklungsabschnitt v1.2 lief in sieben Phasen ab. Jeder Schritt ist mit Uhrzeit im Aktivitätslog "
  "(documentation/project-log/ACTIVITY_LOG.md) festgehalten.")
TABLE(["Phase", "Inhalt", "Ergebnis"], [
    ["1 Bestandsaufnahme", "Alle Quell-, Build- und Dokumentationsdateien gelesen; Werkzeuge geprüft", "Gesamtbild, Prüfliste"],
    ["2 Sicherung", "Git-Branch engineering-v1.2 und Tag baseline-v1.1", "Ausgangsstand wiederherstellbar"],
    ["3 Ausgangsprüfung", "Netzliste, ERC, DRC mit kicad-cli; Leiterbahnbreiten ausgemessen", "0 Fehler; Doku-Abweichung gefunden"],
    ["4 Recherche", "Datenblätter TI, Adafruit, Diodes, onsemi, Omron, PUI; Adafruit-Originalschaltplan", "2 Grenzwertverletzungen, 1 Risiko widerlegt"],
    ["5 Korrektur", "design.py, make_pcb.py, make_sch.py, Software, neue Prüfwerkzeuge", "4 Platinen-Builds, alle Prüfungen bestanden"],
    ["6 Beschaffung", "Preis- und Lieferprüfung bei österreichischen und EU-Händlern", "Lieferengpass Pi Zero 2 W erkannt"],
    ["7 Dokumentation", "Technische Doku, Projekt-Log, dieser Bericht", "documentation/"],
], [1.2, 2.6, 1.6], "Entwicklungsphasen v1.2")
H2("3.1 Arbeitsweise")
P("Alle Änderungen erfolgen an den Quelldateien, nie an erzeugten Dateien (Platine, Gerber, STL). Nach jeder "
  "Änderung läuft der vollständige Build mit Autorouting, ERC und DRC. Weil der Autorouter bei jedem Lauf ein "
  "anderes Layout erzeugt, wurde jedes Ergebnis neu geprüft. Ein Schutzmechanismus (Hook) verhindert das "
  "versehentliche Bearbeiten erzeugter Dateien.")

# =====================================================================
H1("4 Elektronikentwicklung")
H2("4.1 Komponenten und Aufgaben")
TABLE(["Ref.", "Komponente", "Aufgabe", "Schlüsseldaten"], [
    ["J1", "Raspberry Pi Zero 2 W", "Rechner, Emulation", "5 V, typ. 350 mA, Spitze 600 mA"],
    ["J2", "Display ILI9341 2,4\" (≈ MSP2402)", "Anzeige", "SPI, 3,3-V-Logik, 0,57 W"],
    ["J10", "Adafruit PowerBoost 1000C", "Laden + 5,2-V-Wandler", "TPS61090 + MCP73871, 1 A"],
    ["J3", "Adafruit PAM8302", "Lautsprecherverstärker", "24 dB, 1,5 W @ 8 Ω"],
    ["J11/12", "Adafruit ADS1115 (STEMMA QT)", "Akkuspannung messen", "16 Bit, I2C 0x48, 6 MΩ Eingang"],
    ["Q1, Q2", "onsemi BS170", "Ein/Aus-Logik", "V_GS(th) ≤ 3,0 V @ 1 mA"],
    ["D2", "Vishay BAT85", "Pegeltrennung LBO → GPIO", "Schottky, V_F ≈ 0,2 V"],
    ["SW1–8", "Omron B3F-1020", "Tasten", "6 × 6 × 5,0 mm"],
    ["J7", "Same Sky SJ1-3525N", "Kopfhörerbuchse", "Schaltkontakte trennen Lautsprecher"],
    ["RV1", "Bourns PTV09A-2020F-A103", "Lautstärke", "10 kΩ log"],
    ["LS1", "PUI AS02008MR-5-R", "Lautsprecher", "8 Ω, 0,5 W (max. 0,8 W)"],
], [0.6, 1.7, 1.4, 1.6], "Hauptkomponenten")
H2("4.2 Energieversorgung und Strombudget")
P("Der Akku (LiPo 1S, 3,0–4,2 V) speist den PowerBoost, der 5,2 V für Pi, Display und Verstärker erzeugt. Der Pi "
  "erzeugt daraus 3,3 V für Display-Hintergrundlicht, ADC und Pull-ups.")
TABLE(["Verbraucher", "typisch", "Spitze"], [
    ["Pi Zero 2 W (Emulation, WLAN)", "350 mA", "600 mA"],
    ["Display", "115 mA", "115 mA"],
    ["Verstärker + Lautsprecher", "60 mA", "≈ 120 mA (v1.1: ≈ 330 mA)"],
    ["Sonstiges", "5 mA", "5 mA"],
    ["**Summe am 5-V-Ausgang**", "**≈ 530 mA**", "**≈ 840 mA (v1.1: ≈ 1,05 A)**"],
], [2.5, 1, 1.6], "Strombudget (Schätzung aus Datenblättern)")
P("Laufzeit: nutzbare Energie ≈ 6,7 Wh (2000 mAh × 3,7 V × 90 %), Wandlerwirkungsgrad ≈ 85 %. Daraus ergeben sich "
  "≈ 2,1 h typisch, 2,7 h bei sparsamen Emulatoren und 1,5 h unter Dauervolllast.")
H2("4.3 Soft-Power-Schaltung und Nachweis")
P("Der Schalter trennt den Akku nicht direkt. In Stellung EIN zieht er das Gate von Q1 auf Masse, Q1 sperrt und der "
  "EN-Eingang des PowerBoost wird über dessen internen Pull-up aktiv. In Stellung AUS meldet der Schalter dem Pi "
  "über GPIO16 den Abschaltwunsch. Linux fährt herunter und hält währenddessen über GPIO4 und Q2 die Versorgung. "
  "Nach dem Halt fällt GPIO4, R8 schaltet Q1 ein und Q1 zieht EN auf Masse.")
P("Bisher galt die Schaltschwelle von Q1 bei fast leerem Akku als Risiko. Die Auswertung des Original-Schaltplans "
  "von Adafruit (Eagle-Datei Rev B) ergab den EN-Pull-up R13 = 200 kΩ. Q1 muss also höchstens 4,2 V / 200 kΩ = 21 µA "
  "ziehen. Die maximale Schwellenspannung der BS170 von 3,0 V ist laut onsemi bei 1 mA Drainstrom definiert, also bei "
  "fast dem 50-fachen Bedarf. Der EN-Eingang des TPS61090 schaltet unter 0,2 × VBAT ab. Damit ist die Funktion bis "
  "zur Abschaltspannung des Akkus rechnerisch gesichert.")
H2("4.4 Korrektur 1: Unterspannungssignal LBO (R10)")
P("Der LBO-Ausgang des TPS61090 ist ein Open-Drain-Ausgang, laut TI-Datenblatt spezifiziert für 100 µA Low-Strom "
  "bei V_OL ≤ 0,4 V. In v1.1 zog der Pull-up R10 = 10 kΩ zusammen mit dem internen Pull-up des Pi rund 0,37 mA, also "
  "das 3,7-fache des Spezifikationswerts. Damit war ein sicherer Low-Pegel nicht garantiert.")
TABLE(["Größe", "v1.1", "v1.2"], [
    ["R10", "10 kΩ", "100 kΩ"],
    ["Interner Pull-up GPIO20", "an (≈ 50 kΩ)", "aus (gpio=20=ip,pn)"],
    ["Strom in LBO", "≈ 370 µA", "≈ 31 µA ✔"],
    ["Low-Pegel an GPIO20", "nicht garantiert", "≤ 0,6 V < V_IL 0,8 V ✔"],
], [2, 1.5, 1.5], "LBO-Auslegung")
H2("4.5 Korrektur 2: Lautsprecherleistung (R6, R7)")
P("Der PWM-Ausgang des Pi liefert nach dem RC-Filter bei Vollaussteuerung 0,417 V_eff. Über das Mischnetz R6/R7 und "
  "das Lautstärkepoti gelangt das Signal an den PAM8302 mit fester Verstärkung 24 dB (Faktor 15,85). In v1.1 "
  "(R6/R7 = 10 kΩ) ergeben sich am 8-Ω-Lautsprecher bis zu 1,4 W, während der Lautsprecher nur 0,5 W Nenn- und "
  "0,8 W Maximalleistung verträgt.")
TABLE(["R6/R7", "Leistung, Verstärkereingang 10 kΩ", "Leistung, ungünstigster Fall (ohne Last)"], [
    ["10 kΩ (v1.1)", "1,36 W", "1,53 W (Begrenzung) – Überlast"],
    ["22 kΩ", "0,53 W", "1,24 W"],
    ["33 kΩ", "0,29 W", "0,78 W"],
    ["**47 kΩ (v1.2)**", "**0,17 W**", "**0,49 W ✔**"],
], [1.2, 2, 2.2], "Lautsprecherleistung abhängig von R6/R7 (Rechnung)")
P("Mit 47 kΩ bleibt die Nennleistung in jedem Fall eingehalten. Gleichzeitig sinkt die Spitzenlast am 5-V-Netz um "
  "rund 210 mA, damit bleibt der PowerBoost auch im ungünstigsten Fall unter seiner 1-A-Grenze.")
H2("4.6 Korrektur 3: Akkuspannungsmessung")
P("Der ADS1115 hat im Messbereich ±4,096 V eine Gleichtakt-Eingangsimpedanz von 6 MΩ (TI). Sie liegt parallel zum "
  "unteren 100-kΩ-Teilerwiderstand. Der wirksame Teilerfaktor ist deshalb 2,0167 statt 2,000. Ohne Korrektur zeigt "
  "die Software rund 35 mV zu wenig an. Die Korrektur erfolgt in der Software (Kapitel 7), dazu kommt ein "
  "Kalibrierfaktor für den Abgleich mit dem Multimeter.")
H2("4.7 Logikpegel und Kompatibilität")
TABLE(["Schnittstelle", "Pegel", "Bewertung"], [
    ["Pi ↔ Display (SPI)", "3,3 V Logik, Modul-VCC 5 V über eigenen Regler", "kompatibel"],
    ["Pi ↔ ADS1115 (I2C)", "3,3 V, ADC an 3V3, Pull-ups auf dem Modul", "kompatibel"],
    ["ADS1115 AIN0", "max. 2,1 V bei VDD 3,3 V", "innerhalb VDD + 0,3 V"],
    ["LBO (bis 4,2 V) → GPIO", "über Schottky-Diode, nur nach unten ziehend", "GPIO nie über 3,3 V"],
    ["GPIO4 → Q2", "3,3 V Gate, 4,2 µA Last", "ausreichend"],
], [1.5, 2.5, 1.2], "Pegelprüfung")

# =====================================================================
H1("5 PCB-Entwicklung")
H2("5.1 Schaltplan")
P("Der Schaltplan entsteht vollständig aus design.py. Alle Verbindungen laufen über globale Netzlabels. Ein "
  "Prüfskript exportiert nach jedem Lauf die Netzliste und vergleicht jede Pin-Netz-Zuordnung mit der Quelle.")
IMG("documentation/final-report/img/schaltplan.png", CONTENT_W, "Schaltplan GameboyPi Rev 1.2 (KiCad-Export)")
H2("5.2 Leiterplattendaten und Regeln")
TABLE(["Parameter", "Wert"], [
    ["Abmessungen", "78 × 134 mm, Eckradius 3 mm"],
    ["Aufbau", "2 Lagen FR-4, 1,6 mm, 35 µm Kupfer, HASL bleifrei"],
    ["Signalbahnen", "≥ 0,15 mm (überwiegend 0,25 mm), Abstand 0,2 mm"],
    ["Versorgung +5V/GND/VBAT", "1,0 mm (Engstellen ≥ 0,75 mm), Abstand 0,25 mm"],
    ["+3V3", "0,5 mm (Engstelle 0,38 mm)"],
    ["Vias", "0,6/0,3 mm (Signal), 0,8/0,4 mm (Versorgung)"],
    ["Randzone", "1 mm ohne Bahnen und Vias"],
    ["Masseflächen", "GND auf Vorder- und Rückseite"],
], [1.3, 3], "Platinenparameter")
H2("5.3 Leiterbahnberechnung")
P("Die Strombelastbarkeit wurde nach IPC-2221 für Außenlagen berechnet: I = 0,048 · ΔT^0,44 · A^0,725 "
  "(A = Querschnitt in mil²). Die Bahnbreiten wurden im fertigen Layout per Skript ausgemessen.")
TABLE(["Breite", "I bei ΔT = 10 K", "I bei ΔT = 20 K", "Verwendung"], [
    ["0,25 mm", "0,88 A", "1,19 A", "Signale (< 10 mA)"],
    ["0,38 mm", "1,18 A", "1,59 A", "engste Stelle +3V3 (≈ 0,15 A)"],
    ["0,50 mm", "1,45 A", "1,96 A", "+3V3 regulär"],
    ["0,75 mm", "1,94 A", "2,63 A", "engste Stelle +5V/GND"],
    ["1,00 mm", "2,39 A", "3,24 A", "+5V/GND regulär"],
], [1, 1.2, 1.2, 2], "Strombelastbarkeit der Leiterbahnen")
P("Bei der Spitzenlast von 0,84 A hat die engste Versorgungsbahn eine Reserve von mehr als dem 2,3-fachen.")
H2("5.4 Bauteilplatzierung und Routing")
P("Die Bedienelemente liegen auf der Vorderseite an den ergonomischen Positionen des Originals, Pi, Module und die "
  "Ein/Aus-Logik auf der Rückseite. Geroutet wird automatisch mit Freerouting 2.5 (bis zu vier Durchläufe). "
  "Der endgültige Stand hat 604 Leiterbahnsegmente, 25 Vias und keine offene Verbindung. Die engsten Stellen: +5V 1,0 mm, GND/VBAT 0,75 mm, +3V3 0,38 mm (zulässig 1,18 A bei 0,15 A Last).")
IMG2("electronics/assembly/Platine_vorne.png", "electronics/assembly/Platine_hinten.png", 7.6,
     "Bestückte Platine v1.2, Vorder- und Rückseite (KiCad-3D-Rendering; Module ohne 3D-Modell nur als Stiftleisten)")
H2("5.5 ERC- und DRC-Ergebnisse")
TABLE(["Prüfung", "Werkzeug", "Ergebnis (11.11.2026)"], [
    ["Netzliste ↔ Quelle", "check_netlist.py", "keine fehlenden / keine zusätzlichen"],
    ["Electrical Rules Check", "kicad-cli sch erc --severity-all", "**0 Fehler, 0 Warnungen**"],
    ["Design Rules Check", "kicad-cli pcb drc --severity-all", "**0 Fehler**, 0 unverbundene Pads"],
    ["Schaltplan-Parität", "--schematic-parity", "0 Abweichungen"],
    ["DRC-Warnungen", "", "101: 65 Text-Überlappung, 26 Text auf Kupfer, 8 Text am Rand, 2 Wärmefallen mit 1 Steg – kosmetisch bzw. zusätzlich angebunden"],
], [1.5, 1.8, 2.6], "Elektrische und geometrische Prüfungen")
H2("5.6 Fertigungsvorbereitung")
P("Der Build erzeugt Gerber-Daten (X2), Excellon-Bohrdaten (206 durchkontaktierte Bohrungen ab 0,30 mm, 16 "
  "nicht durchkontaktierte), eine Job-Datei und ein Zip-Paket, das automatisch ins Bestellpaket kopiert wird. "
  "Alle Werte liegen innerhalb der Standardregeln von JLCPCB (min. 0,127 mm Bahn/Abstand, min. 0,3 mm Bohrung). "
  "Dazu kommen Bestückungspläne, Pick-&-Place-Daten, eine KiCad-Stückliste und ein STEP-Modell der Platine.")
NOTE("Der Autorouter erzeugt bei jedem Build ein neues Layout. Vor der Bestellung sind die Gerber-Daten im "
     "Online-Viewer des Herstellers zu kontrollieren.", "Wichtig: ")

# =====================================================================
H1("6 3D-Konstruktion")
H2("6.1 Gehäusekonzept")
P("Das Gehäuse besteht aus Vorder- und Rückschale, die an der Platinenebene geteilt sind. Die Platine wird zwischen "
  "Schraubdomen der Vorderschale und Pfosten der Rückschale eingeklemmt. Das Design „GBX“ ist schwarz mit silbernen "
  "und lila Logo-Einlagen, die bei Mehrfarbdruck direkt mitgedruckt werden.")
IMG2("mechanical/previews/design_front.png", "mechanical/previews/design_back.png", 7.0,
     "Gehäuse Vorder- und Rückseite im GBX-Design (OpenSCAD-Vorschau, kein Foto)")
H2("6.2 Abmessungen und Höhenstapel")
TABLE(["Ebene", "z ab Vorderfläche", "Herleitung"], [
    ["Frontwand innen", "2,0 mm", "Wandstärke"],
    ["Displayglas", "2,5 mm", "+ 0,5 mm Moosgummi"],
    ["Platine Vorderseite", "12,1 mm", "+ 9,6 mm Display-Stapel (Touch 1,3 + Klebeband 0,5 + LCD 2,2 + Modul 1,6 + Hülse 4,0)"],
    ["Trennebene", "13,7 mm", "+ 1,6 mm Platine"],
    ["Pi-Oberkante", "26,3 mm", "+ 8,5 mm Buchse + 2,5 mm Stiftleiste + 1,6 mm"],
    ["Rückwand innen", "27,3 mm", "1,0 mm Luft"],
    ["Außen", "29,3 mm", "84 × 140 × 29,3 mm gesamt"],
], [1.4, 1.2, 3.2], "Höhenstapel des Gehäuses")
H2("6.3 Tasten und Display-Integration")
P("Die Tasten werden mit der Druckfläche nach unten gedruckt: Kappe, Flansch und Stößel. Die Stößellänge ergibt sich "
  "aus der durch Omron bestätigten Tasterhöhe von 5,0 mm zu 3,75 mm. Leerweg (0,15 mm) plus Schaltweg (0,25 mm) "
  "sind deutlich kleiner als der Überstand der Kappe (1,6 mm). Das D-Pad hat vier Stößel auf 7,5 mm Radius und eine "
  "Kippnoppe. Das Display sitzt auf zwei 4-mm-Hülsen und wird von einem Rahmen in der Frontschale zentriert.")
H2("6.4 Montage und Verschraubung")
P("Vier Schrauben M2,5 × 20 laufen durch die Rückschale und die Platine und schneiden sich in 2,2-mm-Kernlöcher der "
  "Frontdome. Die Einschraubtiefe beträgt 5,8 mm (≈ 2,3 × Nenndurchmesser), die Domwand 1,9 mm. Der Akku liegt in "
  "einem 4 mm hohen Rahmen der Rückschale und ist nach dem Abnehmen der Rückschale werkzeuglos tauschbar.")
IMG2("mechanical/previews/front.png", "mechanical/previews/back_inside.png", 7.0,
     "Vorderschale (Außenseite, Druckansicht) und Rückschale von innen mit Akkurahmen und Lüftungsschlitzen (OpenSCAD-Rendering)")
H2("6.5 3D-Druck, Material und Toleranzen")
TABLE(["Teil", "Masse (Vollmaterial)", "Druckausrichtung"], [
    ["Vorderschale", "35,7 g", "Sichtseite auf dem Druckbett"],
    ["Rückschale", "43,5 g", "Rückseite auf dem Druckbett"],
    ["Tasten, Knopf, Hülsen, Logo-Einlagen", "5,8 g", "Druckfläche nach unten"],
    ["**Summe**", "**85 g** (real ≈ 60–70 g)", "keine Stützen nötig"],
], [2, 1.5, 2], "Druckteile")
P("Empfohlen: PLA, 0,2 mm Schichthöhe, 3 Wände, 20 % Füllung. Spiel für bewegliche Teile 0,25 mm. Die Prüfung aller "
  "11 STL-Dateien ergab geschlossene Hüllen (0 offene Kanten). Die Kollisionsprüfung von 21 Bauteil-Hüllkörpern "
  "gegen beide Schalen ergab keine Kollision. Ein neues Prüfwerkzeug vergleicht 36 Positionen und Pinbelegungen "
  "zwischen Platine, Gehäuse und Software und meldet jede Abweichung.")
NOTE("Alle 11 Gehäuseteile liegen zusätzlich als STEP-Volumenkörper vor (mechanical/step, erzeugt mit FreeCAD 1.1.4). "
     "Die Körper sind gültig und geschlossen, das Volumen stimmt auf ± 0,004 % mit den Druckdaten überein. Ebene Flächen "
     "sind zusammengefasst, Rundungen bleiben facettiert. Die editierbare Quelle ist weiterhin die OpenSCAD-Datei; "
     "der direkte CSG-Import in FreeCAD scheiterte an den offset()-Extrusionen.", "STEP-Export: ")

# =====================================================================
H1("7 Firmware und Software")
H2("7.1 Plattform")
P("Statt eines Mikrocontrollers arbeitet ein Linux-System (RetroPie 4.8 auf Raspberry Pi OS Buster, 32 Bit). Die "
  "hardwarenahe Software besteht aus Device-Tree-Overlays, dem Display-Treiber fbcp-ili9341 und dem Python-Dienst "
  "battery_monitor.py. Timer, Interrupts und Entprellung der Tasten übernimmt der Linux-Kernel (gpio-key).")
H2("7.2 Treiber und Schnittstellen")
TABLE(["Schnittstelle", "GPIO (BCM)", "Treiber / Parameter"], [
    ["SPI0 Display", "8, 9, 10, 11, DC 25, RST 24", "fbcp-ili9341, DMA, Taktteiler 6"],
    ["I2C1 ADS1115", "2, 3", "smbus, Adresse 0x48, Single-Shot 128 SPS"],
    ["PWM-Audio", "12, 13", "audremap pins_12_13"],
    ["Tasten", "5, 6, 19, 26, 23, 22, 17, 27", "gpio-key (Tastatur-Codes)"],
    ["Ein/Aus", "16, 4", "gpio-shutdown, gpio-poweroff (active_low)"],
    ["Unterspannung", "20", "Eingang ohne Pull, Dienst entprellt"],
    ["Konsole", "14, 15", "UART 115200 Baud"],
], [1.3, 1.8, 2.4], "Software-Schnittstellen")
H2("7.3 Verbesserungen v1.2")
BUL([("Messgenauigkeit: ", "Teilerfaktor mit ADC-Eingangsimpedanz (2,0167) und Kalibrierfaktor VBAT_CAL."),
     ("Robustheit: ", "Unterspannungssignal muss drei Messungen in Folge (15 s) anliegen, Lastspitzen lösen nicht mehr sofort eine Abschaltung aus."),
     ("Spezifikationstreue: ", "interner Pull-up an GPIO20 abgeschaltet (Boot-Konfiguration und Dienst)."),
     ("Testbarkeit: ", "Entscheidungslogik als hardwarefreie Klasse; 7 automatische Tests."),
     ("Installation: ", "install.sh mit strikter Fehlerbehandlung, Root-Prüfung, Wiederanlauf und Upgrade-Pfad.")])
H2("7.4 Ressourcenbedarf")
P("fbcp-ili9341 überträgt per DMA nur geänderte Bildbereiche und belastet einen der vier Kerne nur gering. Der "
  "Akku-Dienst liest alle 5 s einen Messwert und braucht vernachlässigbare CPU-Zeit. Die Pinbelegung aller "
  "Konfigurationsdateien wird automatisch gegen die Platine geprüft.")

# =====================================================================
H1("8 Stückliste und Einkauf")
H2("8.1 Endgültige Stückliste (Auszug)")
TABLE(["Ref.", "Bauteil", "Hersteller-Nr.", "Menge"], [
    ["J1", "Raspberry Pi Zero 2 WH", "SC0721", "1"],
    ["J2", "Display 2,4\" ILI9341 mit Touch", "LAFVIN (≈ MSP2402)", "1"],
    ["J10", "PowerBoost 1000C", "Adafruit 2465", "1"],
    ["J3", "PAM8302", "Adafruit 2130", "1"],
    ["J11/12", "ADS1115 STEMMA QT", "Adafruit 1085", "1"],
    ["BT1", "LiPo 103450 2000 mAh, Schutz, JST-PH", "–", "1"],
    ["LS1", "Lautsprecher 20 mm 8 Ω", "PUI AS02008MR-5-R", "1"],
    ["SW1–8", "Taster 6 × 6 × 5 mm", "Omron B3F-1020", "8"],
    ["SW9 / J7 / RV1", "Schiebeschalter / Klinke / Poti", "C&K OS102011MA1QN1 / SJ1-3525N / PTV09A-2020F-A103", "je 1"],
    ["Q1, Q2 / D2 / D1", "MOSFET / Schottky / LED", "BS170 / BAT85 / LTL-4221N", "2 / 1 / 1"],
    ["R6, R7", "**47 kΩ** (v1.2)", "Yageo MFR-25FBF52-47K", "2"],
    ["R9–R12", "100 kΩ (R10 v1.2)", "Yageo MFR-25FBF52-100K", "4"],
    ["C1 / C3, C5", "470 µF / 100 µF 10 V", "Rubycon 10YXJ470M6.3X11 / Panasonic ECE-A1AKS101", "1 / 2"],
], [1, 2, 2.6, 0.7], "Stückliste (vollständig in FINAL_BOM.md und bom/bill-of-materials.csv)", font=8.5)
H2("8.2 Preis- und Lieferprüfung (11.11.2026)")
TABLE(["Teil", "Händler", "Preis inkl. MwSt.", "Lieferstatus"], [
    ["Pi Zero 2 WH", "BerryBase.at", "20,90 €", "nicht lieferbar"],
    ["Pi Zero 2 WH", "Reichelt", "22,10 €", "widersprüchlich (ab 22.12. bzw. lieferbar)"],
    ["PowerBoost 1000C", "BerryBase.at", "23,90 €", "nicht lieferbar"],
    ["PowerBoost 1000C", "Reichelt.at", "25,16 €", "nicht abrufbar"],
    ["PAM8302", "BerryBase.at", "3,90 €", "nicht lieferbar"],
    ["PAM8302", "Kiwi Electronics (NL)", "≈ 4,43 €", "lagernd laut Suche"],
    ["ADS1115", "BerryBase.at", "15,90 €", "lieferbar (61 Stk.)"],
], [1.4, 1.6, 1.2, 2], "Geprüfte Preise (Auszug)")
P("Ursache des Pi-Engpasses ist laut Fachpresse die knappe Substrat-Fertigung für Chips. Empfohlen wird: Pi bei "
  "Reichelt, Kleinteile und Adafruit-Module in einem DigiKey-Warenkorb (CSV-Upload), ADS1115 bei BerryBase oder "
  "DigiKey, Display, Akku und Schrauben bei Amazon, Platinen bei JLCPCB. Als Ausweichlösung passt der Pi Zero W "
  "ohne Änderung.")
H2("8.3 Gesamtkosten")
TABLE(["Block", "günstig", "teuer"], [
    ["Pi, microSD, Display, Akku", "51,60 €", "63,10 €"],
    ["PowerBoost, PAM8302, ADS1115", "43,70 €", "46,56 €"],
    ["Kleinteile inkl. Lautsprecher", "17 €", "20 €"],
    ["Schrauben, Kleinmaterial", "3 €", "24 €"],
    ["Platinen (5 Stück)", "20 €", "45 €"],
    ["3D-Druck", "2 € (eigener Drucker)", "35 € (Dienstleister)"],
    ["Versand", "10 €", "25 €"],
    ["**Gesamt**", "**≈ 147 €**", "**≈ 259 €**"],
], [2.5, 1.5, 1.5], "Kostenschätzung (typisch ≈ 160–190 €)")
P("Die Montage erfolgt in Eigenleistung (geschätzt 4–6 h Löten und Zusammenbau, 1–2 h Software). Bestellt wurde nichts.")

# =====================================================================
H1("9 Zusammenbau")
steps = [
    "Platinen bestellen, Gehäuse drucken. Zuerst nur die Frontschale probedrucken und Taster, Klinke und Display einlegen.",
    "Bauteile prüfen: ADS1115 in STEMMA-QT-Ausführung, R6/R7 = 47 kΩ, R10 = 100 kΩ.",
    "Vorderseite löten: Widerstände R1–R7, Kondensatoren C2/C4, Elkos C3/C5 (Polarität), LED, Taster, Schalter, Klinke.",
    "Rückseite löten: R8–R12, Diode D2, MOSFETs Q1/Q2, C6, C1, Poti, UART-Leiste, 2 × 20-Buchse, Modul-Stiftleisten.",
    "Beinchen im Akkubereich kürzen und mit Kapton abdecken.",
    "Erstinbetriebnahme ohne Pi: Widerstände an den Testpunkten, dann Akku (Polarität am JST-Stecker messen!) und Abschaltlogik prüfen.",
    "Display auf Abstandshülsen montieren und anlöten, PAM8302 und ADS1115 aufsetzen, Lautsprecher anschließen.",
    "Tasten, Lautsprecher und Platine in die Frontschale, Akku in die Rückschale, Pi aufstecken, verschrauben.",
    "RetroPie 4.8 flashen, install.sh ausführen, Messplan mit Pi abarbeiten, Spannungsanzeige kalibrieren.",
]
for s in steps:
    p = doc.add_paragraph(style="List Number"); p.add_run(s); p.paragraph_format.space_after = Pt(2)
P("Detaillierte Anleitungen: documentation/assembly-guide.md und ASSEMBLY_GUIDE.md (Checkliste).")

# =====================================================================
H1("10 Tests und Qualitätssicherung")
H2("10.1 Durchgeführte Prüfungen")
TABLE(["Bereich", "Prüfung", "Ergebnis"], [
    ["Software", "7 Unit-Tests battery_monitor.py (pytest)", "7/7 bestanden"],
    ["Software", "install.sh: bash -n + ShellCheck 0.11; battery_monitor.py: py_compile", "ok, 0 ShellCheck-Befunde"],
    ["Mechanik", "STEP-Export (FreeCAD 1.1.4) und Rücklesetest", "11/11 gültig, Volumen ± 0,004 %"],
    ["Elektrik", "Netzliste, ERC", "0 Abweichungen, 0/0"],
    ["Leiterplatte", "DRC, Parität, Routing", "0 Fehler, 0 unverbunden, 0 ungeroutet"],
    ["Leiterplatte", "Bahnbreiten, Bohrdaten", "Versorgung ≥ 0,75 mm, Bohrung ≥ 0,30 mm"],
    ["Mechanik", "Kollision 21 Hüllkörper", "0 Kollisionen"],
    ["Mechanik", "STL-Hüllen, Masse", "11/11 geschlossen, 85 g"],
    ["System", "Konsistenz Platine ↔ Gehäuse ↔ Software", "36 Prüfungen, 0 Abweichungen"],
    ["System", "Mutationstest der Konsistenzprüfung", "3/3 eingebaute Fehler erkannt"],
    ["Fertigung", "Gerber-Paket = Bestellpaket", "identisch (MD5)"],
], [1, 3, 2], "Prüfprotokoll v1.2")
H2("10.2 Während der Prüfung gefundene Fehler")
P("Die neuen Unit-Tests fanden einen Randfall in der Teilerformel (unendliche Eingangsimpedanz ergab „NaN“). Die "
  "Formel wurde auf Leitwerte umgestellt. Die Sichtprüfung der Renderings zeigte eine veraltete Versionsbeschriftung "
  "und einen Text über Lötpads. Beides wurde im Generator korrigiert und neu gebaut.")
H2("10.3 Noch erforderliche physische Prüfungen")
BUL(["Versorgung unter Last (5,0–5,3 V, keine Unterspannungsmeldung des Pi)",
     "Abschaltlogik: EN < 0,4 V bei AUS, Halten über GPIO4, Abschalten nach dem Herunterfahren",
     "LBO-Pegel bei 3,0 V Akku und automatische Abschaltung",
     "Akkumessung ± 0,05 V gegen Multimeter",
     "Lautsprecherspannung ≤ 2,0 V_eff bei Vollausschlag, Kopfhörer-Abschaltung",
     "Temperatur nach 30 min Last < 80 °C",
     "Mechanik: Probedruck, Tastengang, Passung von Display, Buchsen und Schrauben",
     "Laufzeitmessung über einen vollständigen Entladezyklus"])

# =====================================================================
H1("11 Probleme und Lösungen")
TABLE(["Problem", "Ursache", "Lösung", "Status"], [
    ["Lautsprecher bis 1,4 W belastbar, Nennwert 0,5 W", "24 dB Verstärkung, niederohmiges Mischnetz", "R6/R7 47 kΩ", "behoben (rechnerisch)"],
    ["LBO-Strom 0,37 mA > 100 µA", "R10 10 kΩ + interner Pull-up", "R10 100 kΩ, Pull aus", "behoben (rechnerisch)"],
    ["Akkuanzeige 0,8 % zu niedrig", "ADC-Eingangsimpedanz 6 MΩ", "Softwarekorrektur + Kalibrierung", "behoben"],
    ["Sofortabschaltung bei kurzem LBO", "keine Entprellung", "3 Messungen in Folge", "behoben"],
    ["Schaltschwelle Q1 unsicher", "EN-Pull-up unbekannt", "Originalschaltplan: 200 kΩ → 21 µA", "geklärt"],
    ["Handübertrag Platine → Gehäuse", "keine Kontrolle", "check_consistency.py", "behoben"],
    ["Doku: Bahnbreite 1,0 mm", "Engstellen 0,75 mm", "nachgemessen, Doku korrigiert", "behoben"],
    ["Pi Zero 2 W nicht lieferbar", "Substrat-Engpass", "Reichelt / Pi Zero W als Fallback", "offen (Markt)"],
    ["Bauhöhen Poti, Klinke, Elkos nicht gemessen", "keine Hardware", "Probedruck vor Serie", "offen"],
], [1.8, 1.4, 1.6, 1], "Probleme und Lösungen", font=8.5)

# =====================================================================
H1("12 Endergebnis")
P("Version 1.2 ist ein vollständig dokumentierter, fertigungsreifer Entwurf. Alle automatisch prüfbaren Kriterien "
  "sind erfüllt: Netzliste, ERC und DRC fehlerfrei, keine Kollision im Gehäuse, alle Druckteile geschlossen, "
  "Platine, Gehäuse und Software stimmen überein, und die Akku-Software ist durch Tests abgesichert. Zwei "
  "Grenzwertverletzungen aus v1.1 sind rechnerisch behoben, ein als kritisch eingestuftes Risiko ist durch "
  "Herstellerdaten entkräftet.")
TABLE(["Kategorie", "Inhalt"], [
    ["Abgeschlossen und verifiziert", "Platinen-Build v1.2 (ERC/DRC), Gerber, Software-Tests, Konsistenz, STL-Prüfung"],
    ["Rechnerisch nachgewiesen", "Strombudget, Leiterbahnen, Soft-Power, LBO, Audioleistung, Schraubverbindung"],
    ["Simuliert / gerendert", "3D-Ansichten von Platine und Gehäuse (keine Fotos)"],
    ["Vorgeschlagen", "Gewindeeinsätze, USB-C, Schultertasten, Akkuanzeige im Bild"],
    ["Nicht verifiziert", "jede physische Funktion – das Gerät ist nicht gebaut"],
], [1.7, 4], "Einordnung der Ergebnisse")

# =====================================================================
H1("13 Ausblick")
BUL(["Prototyp aufbauen und den Messplan abarbeiten; Ergebnisse in TEST_RESULTS.md eintragen.",
     "Akkuanzeige als Bildschirm-Overlay (pngview, Daten aus /dev/shm/battery).",
     "Gewindeeinsätze M2,5 für häufiges Öffnen.",
     "USB-C-Ladebuchse über ein anderes Lademodul.",
     "Schultertasten L/R über die freien GPIOs 7, 18 und 21.",
     "Manuelles Nachrouten der Audio- und SPI-Bereiche nach einer Rauschmessung.",
     "Gehäuse als Feature-Modell in FreeCAD/CadQuery mit echten Rundungen (facettierte STEP-Körper liegen bereits vor).",
     "Langfristig: Bookworm-kompatibler Display-Treiber oder I2S-Audio."])

# =====================================================================
H1("14 Quellenverzeichnis")
P("Alle Quellen wurden am 11.11.2026 abgerufen. Vollständige Liste mit Prüfstatus: documentation/project-log/RESEARCH_SOURCES.md.")
srcs = [
    "Texas Instruments: TPS6109x Synchronous Boost Converter, Datenblatt. https://www.ti.com/lit/ds/symlink/tps61090.pdf",
    "Texas Instruments: ADS111x Ultra-Small 16-Bit ADC, Datenblatt. https://www.ti.com/lit/ds/symlink/ads1115.pdf",
    "Adafruit: PowerBoost 1000C, Schaltplan Rev B (Eagle). https://github.com/adafruit/Adafruit-PowerBoost-1000C",
    "Adafruit: PowerBoost 1000C – Pinouts. https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/pinouts",
    "Adafruit: Mono 2.5W Class D Audio Amplifier – PAM8302, Produktseite. https://www.adafruit.com/product/2130",
    "Diodes Inc.: PAM8302A, Datenblatt. https://cdn-shop.adafruit.com/datasheets/PAM8302A.pdf",
    "onsemi: BS170 / MMBF170, Datenblatt. https://www.onsemi.com/download/data-sheet/pdf/mmbf170-d.pdf",
    "Omron: B3F Tactile Switch, Datenblatt. https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf",
    "PUI Audio: AS02008MR-5-R, Spezifikation. https://puiaudio.com/file/specs-AS02008MR-5-R.pdf",
    "juj: fbcp-ili9341, README. https://github.com/juj/fbcp-ili9341",
    "IPC-2221: Generic Standard on Printed Board Design (Strombelastbarkeit, Formel).",
    "BerryBase, Reichelt, Kiwi Electronics, Botland: Produktseiten (Preise und Lieferstatus 11.11.2026).",
    "raspberry.tips: Raspberry Pi Zero 2 W ausverkauft: Alternativen 2026 (Stand 08.11.2026).",
]
for s in srcs:
    p = doc.add_paragraph(style="List Number 2"); r = p.add_run(s); r.font.size = Pt(9); p.paragraph_format.space_after = Pt(2)

os.makedirs(OUT_DIR, exist_ok=True)
doc.save(OUT)
print("gespeichert:", OUT, "| Abbildungen:", fig_no[0], "| Tabellen:", tab_no[0])
