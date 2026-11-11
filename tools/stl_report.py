"""STL-Prüfung für die Gehäuseteile: geschlossene Hülle, Maße, Volumen, Masse.

Nur Standardbibliothek. Aufruf aus der Repo-Wurzel:  python tools/stl_report.py
Geschlossen = jede Kante gehört zu genau zwei Dreiecken (2-Mannigfaltigkeit, wasserdicht).
"""
import collections
import glob
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLA_DENSITY = 1.24  # g/cm³


def read_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    tris = []
    if data[:5] == b"solid" and b"facet" in data[:400]:
        verts = []
        for line in data.decode("ascii", "replace").splitlines():
            p = line.split()
            if p and p[0] == "vertex":
                verts.append(tuple(float(v) for v in p[1:4]))
                if len(verts) == 3:
                    tris.append(tuple(verts))
                    verts = []
    else:
        n = struct.unpack_from("<I", data, 80)[0]
        for i in range(n):
            v = struct.unpack_from("<12f", data, 84 + 50 * i)
            tris.append((v[3:6], v[6:9], v[9:12]))
    return tris


def analyse(tris):
    key = lambda p: (round(p[0], 4), round(p[1], 4), round(p[2], 4))
    edges = collections.Counter()
    vol = 0.0
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for a, b, c in tris:
        ka, kb, kc = key(a), key(b), key(c)
        for e in ((ka, kb), (kb, kc), (kc, ka)):
            edges[tuple(sorted(e))] += 1
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        for p in (a, b, c):
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    open_edges = sum(1 for n in edges.values() if n != 2)
    return dict(tris=len(tris), open_edges=open_edges, vol_cm3=abs(vol) / 1000.0,
                size=[hi[i] - lo[i] for i in range(3)], zmin=lo[2])


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "mechanical", "stl", "*.stl")))
    total = 0.0
    bad = 0
    print("%-22s %8s %6s %22s %8s %7s" % ("Teil", "Dreiecke", "offen", "Maße x×y×z [mm]", "cm³", "g PLA"))
    for f in files:
        r = analyse(read_stl(f))
        g = r["vol_cm3"] * PLA_DENSITY
        total += g
        bad += r["open_edges"] > 0
        print("%-22s %8d %6d %22s %8.1f %7.1f" % (os.path.basename(f), r["tris"], r["open_edges"],
              "%.1f×%.1f×%.1f" % tuple(r["size"]), r["vol_cm3"], g))
    print("Summe Vollmaterial: %.0f g PLA (100 %% Füllung; real mit 3 Wänden/20 %% Infill weniger)" % total)
    print("Nicht geschlossene Teile: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
