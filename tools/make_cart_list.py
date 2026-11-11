"""Erzeugt die Word-Liste der Warenkörbe (Amazon, DigiKey, JLCPCB) mit Preisen und je einem Sammel-Link.

Stand der Daten: 11.11.2026, direkt aus den Warenkörben im Browser ausgelesen.
Aufruf: python tools/make_cart_list.py [Zielpfad.docx]
"""
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expanduser("~"), "Documents", "Emulator",
                                                         "GameboyPi_Warenkoerbe.docx")
PURPLE = RGBColor(0x4B, 0x2C, 0x82)
GREY = RGBColor(0x55, 0x55, 0x55)
FONT = "Calibri"

AMAZON_CART = "https://www.amazon.de/gp/cart/view.html"
DIGIKEY_SHARE = "https://www.digikey.at/short/f3b0w9n4"
DIGIKEY_CART = "https://www.digikey.at/ordering/shoppingcart"
JLCPCB_QUOTE = "https://cart.jlcpcb.com/quote"

amazon = [
    ("LAFVIN 2,4\" TFT ILI9341 SPI mit Touch", "Display", 16.13),
    ("Verbatim Premium microSDHC 32 GB", "System", 12.14),
    ("GeeekPi 220-tlg. M2,5-Set (11-mm-Bolzen)", "Pi befestigen", 12.10),
    ("Ewwtrey 260-tlg. M3-Nylon-Set", "Display befestigen", 7.04),
    ("Kozelo 30 × M2,5 × 20 Zylinderschrauben", "Gehäuse", 4.63),
    ("BOBOZHONG Kapton-Band 10 mm × 33 m", "Akku isolieren", 4.73),
    ("sourcing map Schaumband 5 mm × 1 mm", "Polster Display", 6.24),
]
amazon_saved = [
    ("2er-Set LiPo 103450 2000 mAh, JST 2,0", "Akku", 13.90, "derzeit nicht auf Lager"),
    ("Litzen-Set 0,14 mm², 10 Farben", "Lautsprecherkabel", 16.39, "auf Lager"),
]
digikey = [
    ("ADS1115 ADC (Adafruit)", "1085", 1, 13.13),
    ("Schiebeschalter", "OS102011MA1QN1", 1, 0.66),
    ("Klinkenbuchse 3,5 mm", "SJ1-3525N", 1, 1.08),
    ("Poti 10 k log", "PTV09A-2020F-A103", 1, 1.08),
    ("Taster 6 × 6 × 5 mm", "B3F-1020", 10, 3.20),
    ("MOSFET", "BS170", 3, 1.20),
    ("Lautsprecher 20 mm 8 Ω", "AS02008MR-5-R", 1, 3.22),
    ("Buchsenleiste 2 × 20", "PPTC202LFBN-RC", 1, 1.88),
    ("Stiftleiste 1 × 3", "PRPC003SAAN-RC", 1, 0.09),
    ("Widerstand 1 kΩ", "MFR-25FBF52-1K", 2, 0.18),
    ("Widerstand 270 Ω", "MFR-25FBF52-270R", 3, 0.27),
    ("Widerstand 150 Ω", "MFR-25FBF52-150R", 3, 0.27),
    ("Widerstand 1 MΩ", "MFR-25FBF52-1M", 2, 0.18),
    ("PowerBoost 1000C (Adafruit)", "2465", 1, 17.52),
    ("PAM8302 Verstärker (Adafruit)", "2130", 1, 3.47),
    ("Schottky-Diode", "BAT85S-TAP", 2, 0.88),
    ("Kondensator 33 nF", "K333K15X7RF5TL2", 3, 0.78),
    ("Kondensator 100 nF", "K104K15X7RF5TL2", 2, 0.54),
    ("Widerstand 100 kΩ", "MFR-25FBF52-100K", 10, 0.37),
    ("Elko 100 µF 10 V", "ECE-A1AKS101", 3, 0.96),
    ("Elko 470 µF 10 V", "10YXJ470M6.3X11", 1, 0.30),
    ("LED rot 3 mm (lieferbar ab 16.11.2026)", "LTL-4221N", 2, 0.34),
    ("Widerstand 47 kΩ 5 % (R6/R7, neu)", "Stackpole CF14JT47K0", 10, 0.24),
]


def eur(v):
    return ("%.2f €" % v).replace(".", ",")


doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
for cs in doc.settings.element.iter(qn("w:compatSetting")):
    if cs.get(qn("w:name")) == "compatibilityMode":
        cs.set(qn("w:val"), "15")
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin = sec.bottom_margin = Cm(1.8)
W = 17.0


def link(paragraph, url, text=None):
    r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "1F5FBF"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text or url; t.set(qn("xml:space"), "preserve"); r.append(t)
    h.append(r)
    paragraph._p.append(h)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), color)
    tcPr.append(s)


def heading(text, size=15):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = PURPLE
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.keep_with_next = True
    return p


def table(header, rows, widths, bold_last=False, right_cols=()):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(255, 255, 255)
        shade(c, "4B2C82")
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(v)); r.font.size = Pt(9.5)
            if bold_last and ri == len(rows) - 1:
                r.bold = True
            if i in right_cols:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if ri % 2 == 1:
                shade(cells[i], "F1EDF8")
    tot = sum(widths)
    for row in t.rows:
        for i, c in enumerate(row.cells):
            c.width = Cm(W * widths[i] / tot)
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(0)
    doc.add_paragraph()


def link_line(label, url):
    p = doc.add_paragraph()
    p.add_run(label).bold = True
    link(p, url)
    return p


# ---- Kopf ----
p = doc.add_paragraph()
r = p.add_run("GameboyPi – Warenkörbe"); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = PURPLE
p = doc.add_paragraph()
r = p.add_run("Stand 11.11.2026, direkt aus den Warenkörben ausgelesen. Bestellt ist nichts. "
              "Pro Shop gibt es einen Link, der alle Artikel zusammen öffnet.")
r.font.color.rgb = GREY

# ---- Amazon ----
a_sum = sum(x[2] for x in amazon)
heading("1. Amazon – 7 Artikel im Warenkorb, %s" % eur(a_sum))
link_line("Link (alle Artikel): ", AMAZON_CART)
table(["Artikel", "Wofür", "Preis"],
      [(n, w, eur(v)) for n, w, v in amazon] + [("Summe Warenkorb", "", eur(a_sum))],
      [9, 4, 2], bold_last=True, right_cols=(2,))
p = doc.add_paragraph("Unter „Für später gespeichert“ (unten im Amazon-Warenkorb, mit „In den Einkaufswagen“ zurückholen):")
s_sum = sum(x[2] for x in amazon_saved)
table(["Artikel", "Wofür", "Preis", "Hinweis"],
      [(n, w, eur(v), h) for n, w, v, h in amazon_saved] + [("Summe gemerkt", "", eur(s_sum), "")],
      [7, 3, 2, 4], bold_last=True, right_cols=(2,))

# ---- DigiKey ----
d_sum = round(sum(x[3] for x in digikey), 2)
heading("2. DigiKey – 23 Positionen, %s + 25,00 € Versand" % eur(d_sum))
link_line("Link (Kopie mit allen 23 Teilen): ", DIGIKEY_SHARE)
link_line("Dein Warenkorb: ", DIGIKEY_CART)
table(["#", "Teil", "Herstellernr.", "Menge", "Preis"],
      [(i + 1, n, pn, q, eur(v)) for i, (n, pn, q, v) in enumerate(digikey)] + [("", "Zwischensumme", "", "", eur(d_sum))],
      [0.8, 6.5, 5, 1.4, 2], bold_last=True, right_cols=(3, 4))
doc.add_paragraph("Geändert am 11.11.2026: 10-kΩ-Widerstände entfernt (in v1.2 nicht mehr nötig). Für R6/R7 kam 47 kΩ dazu: "
                  "Der vorgesehene Yageo MFR-25FBF52-47K wäre erst ab 17.03.2027 lieferbar, deshalb der sofort lieferbare "
                  "Stackpole CF14JT47K0 (5 %, 2,3 × 6,0 mm, passt auf die Platine). 10 Stück kosten 0,24 € und sind billiger als 4 Stück.")
doc.add_paragraph("Versand: 25,00 €, ab 75 € Warenwert gratis (es fehlen %s). Gesamt mit Versand: %s."
                  % (eur(75 - d_sum), eur(d_sum + 25)))

# ---- JLCPCB ----
heading("3. JLCPCB – Platine")
doc.add_paragraph("Nicht auslesbar: Im Browser bist du bei JLCPCB nicht angemeldet. Am 21.10.2026 lag die Platine für 10,40 $ "
                  "im Warenkorb, das war aber noch die alte v1.1. Die neue v1.2 dort hochladen: "
                  "GameboyPi\\bestellung\\1_platine_JLCPCB\\GameboyPi_Gerber.zip")
link_line("Link (Gerber hochladen): ", JLCPCB_QUOTE)

# ---- Gesamt ----
heading("Gesamt (ohne Pi, Platine und 3D-Druck)")
table(["Shop", "Betrag"],
      [("Amazon (Warenkorb)", eur(a_sum)), ("Amazon (gemerkt: Akku + Litze)", eur(s_sum)),
       ("DigiKey inkl. Versand", eur(d_sum + 25)), ("Summe", eur(a_sum + s_sum + d_sum + 25))],
      [6, 2], bold_last=True, right_cols=(1,))
doc.add_paragraph("Noch in keinem Warenkorb: Raspberry Pi Zero 2 WH (derzeit überall knapp) und der 3D-Druck des Gehäuses.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print("gespeichert:", OUT, "| Amazon", eur(a_sum), "| gemerkt", eur(s_sum), "| DigiKey", eur(d_sum))
