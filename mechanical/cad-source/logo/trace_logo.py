"""Vektorisiert das GBX-Logo (gbx_logo_source.jpeg) zu OpenSCAD-Polygonen -> gbx_logo.scad

  "GB" = silberne Pixel (hell, wenig Farbsättigung), "X" = lila Pixel (Blau deutlich über Grün).
  Ausgabe in Logo-Einheiten: Breite des Schriftzugs "GBX" = 100, Ursprung in der Mitte.

Benötigt numpy, scikit-image, pymupdf (zum Lesen des JPEG):
  python -m pip install --target <ordner> scikit-image pymupdf
"""
import os
import sys

import numpy as np
import pymupdf
from skimage import filters, measure, morphology

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gbx_logo_source.jpeg")
OUT = os.path.join(HERE, "gbx_logo.scad")

pm = pymupdf.Pixmap(SRC)
img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3].astype(float)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
bright = img.max(axis=2)

Y0, Y1 = 250, 540                                 # Band des Schriftzugs "GBX"
band = np.zeros(bright.shape, bool)
band[Y0:Y1] = True
purple = band & (b - g > 45) & (bright > 120)
silver = band & (bright > 85) & (b - g < 30)   # Glühen/Innenflächen <= 76, dunkelste Chromkante ~90


def clean(mask, min_size, bridge=2):
    mask = morphology.remove_small_objects(mask, min_size)
    # dünne dunkle Spiegelungsstreifen im Chrom überbrücken, aber nicht in den dunklen Hintergrund wachsen
    # je Buchstabe einzeln schließen, damit nichts zum Nachbarbuchstaben überbrückt wird
    lab = measure.label(mask)
    closed = np.zeros_like(mask)
    for reg in measure.regionprops(lab):
        r0, c0, r1, c1 = reg.bbox
        pad = bridge + 2
        sub = np.pad(lab[r0:r1, c0:c1] == reg.label, pad)
        sub = morphology.binary_closing(sub, morphology.disk(bridge))[pad:-pad, pad:-pad]
        closed[r0:r1, c0:c1] |= sub
    mask = closed & (bright > 40)
    # Löcher füllen, die heller als echte Innenflächen sind (Spiegelungsflecken im Chrom);
    # die Innenflächen des B sind dunkel (Hintergrund) und bleiben offen
    holes = measure.label(~mask, connectivity=1)
    for reg in measure.regionprops(holes, intensity_image=bright):
        touches_border = reg.bbox[0] == 0 or reg.bbox[1] == 0 or reg.bbox[2] == mask.shape[0] or reg.bbox[3] == mask.shape[1]
        if not touches_border and (reg.area < 800 or reg.intensity_mean > 60):
            mask[holes == reg.label] = True
    return mask


purple = clean(purple, 2000)
silver = clean(silver, 2000, bridge=14)

ys, xs = np.nonzero(silver | purple)
x_min, x_max, y_min, y_max = xs.min(), xs.max(), ys.min(), ys.max()
scale = 100.0 / (x_max - x_min)
cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
print("Logo-Pixel: x %d..%d  y %d..%d  -> Seitenverhältnis %.3f" % (x_min, x_max, y_min, y_max,
                                                                   (x_max - x_min) / (y_max - y_min)))


def contours(mask):
    smooth = filters.gaussian(mask.astype(float), sigma=1.2)
    padded = np.pad(smooth, 2)
    paths = []
    for c in measure.find_contours(padded, 0.5):
        c = measure.approximate_polygon(c, tolerance=0.7)
        if len(c) < 4:
            continue
        pts = [((col - 2 - cx) * scale, -(row - 2 - cy) * scale) for row, col in c]
        paths.append(pts)
    return paths


def scad_module(name, paths):
    pts, idx = [], []
    for p in paths:
        start = len(pts)
        pts.extend(p)
        idx.append(list(range(start, start + len(p))))
    body = ",".join("[%.3f,%.3f]" % q for q in pts)
    return "module %s() {\n  polygon(points=[%s],\n          paths=%s);\n}\n" % (name, body, idx)


with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("// automatisch erzeugt von trace_logo.py aus gbx_logo_source.jpeg – nicht von Hand bearbeiten\n")
    f.write("// Logo-Einheiten: Breite GBX = 100, Ursprung Mitte. Höhe = %.2f\n" % ((y_max - y_min) * scale))
    f.write("gbx_logo_height = %.3f;\n" % ((y_max - y_min) * scale))
    f.write(scad_module("gbx_gb", contours(silver)))
    f.write(scad_module("gbx_x", contours(purple)))
    f.write("module gbx_logo() { gbx_gb(); gbx_x(); }\n")
print("geschrieben:", OUT, "Konturen GB/X:", len(contours(silver)), len(contours(purple)))
sys.exit(0)
