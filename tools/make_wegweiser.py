"""Baut den Wegweiser (Documents/Emulator/Wegweiser.html) als eigenständige Mini-App.

Der Browser darf aus einer lokalen Seite keine Dateien nachladen. Darum bettet dieses Skript
alles ein, was die Seite schön anzeigen soll:
  * Ordnerlisten (Name, Art, Größe, Datum) für GameboyPi, Emulator und Desktop-Archiv
  * Markdown-Dokumente, gerendert zu HTML (Tabellen, Code, Inhaltsverzeichnis)
  * CSV als Tabelle, Quelltexte (.py, .scad, .sh …) als Code
Bilder, Word, PDF, STL usw. verlinkt die Seite direkt (file:///).

Aufruf (Repo-Wurzel):  python tools/make_wegweiser.py
Benötigt: pip install markdown
"""
import csv
import datetime
import html
import io
import json
import os
import posixpath
import re

import markdown

HOME = os.path.expanduser("~")
DOCS = os.path.join(HOME, "Documents")
ROOTS = {
    "GameboyPi": os.path.join(DOCS, "GameboyPi"),
    "Emulator": os.path.join(DOCS, "Emulator"),
    "Desktop-Archiv": os.path.join(HOME, "OneDrive", "Dokumenty", "Desktop-Archiv"),
}
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wegweiser_template.html")
OUT = os.path.join(DOCS, "Emulator", "Wegweiser.html")

SKIP_DIRS = {".git", "__pycache__", "freerouting", ".claude", ".vscode", "node_modules", "build", "img"}
SKIP_FILES = {"desktop.ini", "Thumbs.db"}
TEXT_EXT = {".py", ".scad", ".sh", ".append", ".service", ".txt", ".rpt", ".json", ".ps1", ".js",
            ".gitignore", ".gitattributes", ".kicad_dru"}
MAX_TEXT = 80_000

# Kurzbeschreibungen für bekannte Ordner (erscheinen über der Dateiliste)
DESCR = {
    "GameboyPi": "Das ganze Projekt (Git-Repo, auf GitHub gesichert). Start: README.md",
    "GameboyPi/bestellung": "Alles zum Bestellen: Platine, Bauteile, 3D-Druck, Warenkörbe",
    "GameboyPi/bestellung/1_platine_JLCPCB": "Gerber.zip bei JLCPCB hochladen, Einstellungen in der Anleitung",
    "GameboyPi/bestellung/2_bauteile": "DigiKey/Mouser-CSV zum Hochladen und Einkaufsliste",
    "GameboyPi/bestellung/3_3d_druck": "Die 11 Druckteile (STL) und die Farbliste",
    "GameboyPi/documentation": "Anleitungen und Wissen: Übersicht, Technik, Stückliste, Montage, Tests",
    "GameboyPi/documentation/project-log": "Was wann gemacht wurde: Log, Entscheidungen, Changelog, Tests, Quellen",
    "GameboyPi/documentation/final-report": "Der Projektbericht als Word und PDF",
    "GameboyPi/electronics": "Die Platine (wird aus design.py erzeugt)",
    "GameboyPi/electronics/kicad-project": "Quelle der Platine: design.py. Die KiCad-Dateien werden daraus erzeugt",
    "GameboyPi/electronics/gerber": "Fertigungsdaten für den Platinenhersteller (erzeugt)",
    "GameboyPi/electronics/assembly": "Bestückungspläne, 3D-Bilder, STEP der Platine (erzeugt)",
    "GameboyPi/electronics/schematics": "Der Schaltplan als PDF",
    "GameboyPi/mechanical": "Das Gehäuse (wird aus der .scad-Datei erzeugt)",
    "GameboyPi/mechanical/cad-source": "Quelle des Gehäuses: gameboy_pi_case.scad",
    "GameboyPi/mechanical/stl": "Die Druckdateien (erzeugt)",
    "GameboyPi/mechanical/step": "Gehäuseteile als STEP für andere CAD-Programme (erzeugt, nicht auf GitHub)",
    "GameboyPi/mechanical/previews": "Vorschaubilder des Gehäuses",
    "GameboyPi/software": "Alles für den Raspberry Pi",
    "GameboyPi/software/configuration": "Diese Dateien kommen auf den Pi (install.sh ausführen)",
    "GameboyPi/tools": "Prüf- und Erzeugungsskripte (auch als VS-Code-Tasks)",
    "Emulator": "Dein Startpunkt: Bericht, Warenkorb-Liste und dieser Wegweiser",
    "Desktop-Archiv": "Alte Desktop-Verknüpfungen",
}


def key_to_abs(key):
    root, _, rest = key.partition("/")
    return os.path.join(ROOTS[root], *rest.split("/")) if rest else ROOTS[root]


def file_url(abs_path):
    return "file:///" + abs_path.replace("\\", "/")


def kind(name):
    n = name.lower()
    ext = os.path.splitext(n)[1]
    if n == "readme.md" or ext == ".md":
        return "md"
    for k, exts in {"word": {".docx", ".doc"}, "pdf": {".pdf"}, "img": {".png", ".jpg", ".jpeg", ".webp", ".gif"},
                    "cad": {".stl", ".step", ".stp"}, "zip": {".zip"}, "csv": {".csv"}, "py": {".py"},
                    "scad": {".scad"}, "kicad": {".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_prl"},
                    "gerber": {".gbl", ".gtl", ".gbs", ".gts", ".gbo", ".gto", ".gbp", ".gtp", ".gm1", ".drl", ".gbrjob"},
                    "link": {".lnk", ".url"}, "html": {".html"}}.items():
        if ext in exts:
            return k
    if ext in TEXT_EXT or n in TEXT_EXT:
        return "code"
    return "file"


# ---------------- Markdown ----------------
md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                       extension_configs={"toc": {"permalink": False}})
LINK_RE = re.compile(r'(href|src)="([^"]+)"')


def rewrite_links(html_text, key, all_docs, all_dirs):
    base = posixpath.dirname(key)

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^[a-z]+:", url) or url.startswith("//"):
            return m.group(0)                      # http, mailto, file …
        if url.startswith("#"):
            return '%s="#/doc/%s@%s"' % (attr, key, url[1:])
        path, _, anchor = url.partition("#")
        target = posixpath.normpath(posixpath.join(base, path)).rstrip("/")
        if attr == "href" and target in all_docs:
            return 'href="#/doc/%s%s"' % (target, "@" + anchor if anchor else "")
        if attr == "href" and target in all_dirs:
            return 'href="#/ordner/%s"' % target
        try:
            return '%s="%s"' % (attr, file_url(key_to_abs(target)))
        except KeyError:
            return m.group(0)
    return LINK_RE.sub(fix, html_text)


def render_csv(text):
    sample = text[:2000]
    delim = ";" if sample.count(";") > sample.count(",") else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    if not rows:
        return "<p>(leer)</p>"
    out = ["<table><thead><tr>"] + ["<th>%s</th>" % html.escape(c) for c in rows[0]] + ["</tr></thead><tbody>"]
    for r in rows[1:]:
        out.append("<tr>" + "".join("<td>%s</td>" % html.escape(c) for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def first_heading(text, fallback):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def main():
    dirs, docs = {}, {}
    text_files = []
    for root, top in ROOTS.items():
        if not os.path.isdir(top):
            continue
        for cur, subdirs, files in os.walk(top):
            subdirs[:] = sorted(d for d in subdirs if d not in SKIP_DIRS and not d.startswith("."))
            rel = os.path.relpath(cur, top).replace("\\", "/")
            key = root if rel == "." else root + "/" + rel
            entries = []
            for d in subdirs:
                p = os.path.join(cur, d)
                n_items = len([x for x in os.listdir(p) if x not in SKIP_FILES and not x.startswith(".")])
                entries.append({"n": d, "t": "dir", "c": n_items,
                                "m": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d.%m.%Y")})
            for f in sorted(files, key=str.lower):
                if f in SKIP_FILES or f.startswith("~$"):
                    continue
                p = os.path.join(cur, f)
                k = kind(f)
                entries.append({"n": f, "t": k, "s": os.path.getsize(p),
                                "m": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d.%m.%Y %H:%M"),
                                "u": file_url(p)})
                if k in ("md", "csv", "py", "scad", "code") and os.path.getsize(p) <= MAX_TEXT:
                    text_files.append((key + "/" + f, p, k))
            dirs[key] = {"e": entries, "d": DESCR.get(key, ""), "u": file_url(cur)}

    doc_keys = {k for k, _, _ in text_files}
    for key, p, k in text_files:
        with open(p, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        name = posixpath.basename(key)
        if k == "md":
            md.reset()
            body = md.convert(text)
            body = rewrite_links(body, key, doc_keys, set(dirs))
            toc = [(t["id"], t["name"], t["level"]) for t in md.toc_tokens_flat()] if hasattr(md, "toc_tokens_flat") else []
            if not toc:
                def walk(tokens):
                    for t in tokens:
                        yield (t["id"], t["name"], t["level"])
                        yield from walk(t.get("children", []))
                toc = list(walk(md.toc_tokens))
            docs[key] = {"title": first_heading(text, name), "html": body,
                         "toc": [t for t in toc if t[2] in (2, 3)], "k": "md"}
        elif k == "csv":
            docs[key] = {"title": name, "html": render_csv(text), "toc": [], "k": "csv"}
        else:
            docs[key] = {"title": name, "html": "<pre><code>%s</code></pre>" % html.escape(text), "toc": [], "k": "code"}
        docs[key]["u"] = file_url(p)
        docs[key]["lines"] = text.count("\n") + 1

    data = {"generated": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            "roots": {k: file_url(v) for k, v in ROOTS.items()}, "dirs": dirs, "docs": docs}
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = tpl.replace("/*__DATA__*/null", blob)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("Wegweiser: %s | %d Ordner, %d Dokumente, %d KB" % (OUT, len(dirs), len(docs), len(page) // 1024))


if __name__ == "__main__":
    main()
