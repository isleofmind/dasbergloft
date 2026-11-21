#!/usr/bin/env python3
"""Baut aus den gesicherten Lovable-Seiten (raw/) eine eigenständige statische Website (site/).

Aufruf:  python3 build.py
Ergebnis: site/  -> kann 1:1 auf Cloudflare Pages, Netlify, GitHub Pages o. ä. hochgeladen werden.
"""
import html
import json
import os
import re
import shutil
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "docs")  # GitHub Pages veröffentlicht den Ordner docs/
DOMAIN = "https://dasbergloft.de"
TODAY = datetime.date.today().isoformat()

# Quell-Datei -> (Ausgabe-Datei, URL-Pfad)
PAGES = {
    "index.html": ("index.html", "/"),
    "reisetipps.html": ("reisetipps.html", "/reisetipps"),
    "reisetipps_baden-chiemsee.html": ("reisetipps/baden-chiemsee.html", "/reisetipps/baden-chiemsee"),
    "reisetipps_wandern-chiemgau.html": ("reisetipps/wandern-chiemgau.html", "/reisetipps/wandern-chiemgau"),
    "reisetipps_aktivitaeten-chiemgau.html": ("reisetipps/aktivitaeten-chiemgau.html", "/reisetipps/aktivitaeten-chiemgau"),
    "reisetipps_restaurants-chiemsee.html": ("reisetipps/restaurants-chiemsee.html", "/reisetipps/restaurants-chiemsee"),
    "reisetipps_schlechtwetter-chiemsee.html": ("reisetipps/schlechtwetter-chiemsee.html", "/reisetipps/schlechtwetter-chiemsee"),
    "impressum.html": ("impressum.html", "/impressum"),
}

# SEO: Titel/Beschreibungen mit den wichtigsten Suchbegriffen (Ferienwohnung, Bernau, Chiemsee)
SEO = {
    "/": {
        "title": "Ferienwohnung Bernau am Chiemsee mit Bergblick | Das Bergloft",
        "description": "Ferienwohnung in Bernau am Chiemsee: 80 m², 2 Schlafzimmer, bis 4 Gäste, "
                       "2 Balkone mit Bergblick, 15 Gehminuten zum See. Nachhaltig kernsaniert – direkt anfragen.",
    },
    "/reisetipps": {
        "title": "Reisetipps Chiemsee & Chiemgau | Ferienwohnung Das Bergloft Bernau",
    },
}

ASSET_RE = re.compile(r"/__l5e/assets-v1/[0-9a-f-]{36}/([^\"'`\s,?)<]+)")


def asset_path(m):
    name = m.group(1)
    folder = "fonts" if name.endswith(".otf") else "img"
    return f"/{folder}/{name}"


def meta(s, attr, key):
    m = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ""


def esc(t):
    return html.escape(t, quote=True)


def build_head(src_head, path):
    title = html.unescape(re.search(r"<title>(.*?)</title>", src_head, re.S).group(1))
    desc = meta(src_head, "name", "description")
    og_title = meta(src_head, "property", "og:title") or title
    og_desc = meta(src_head, "property", "og:description") or desc
    og_type = meta(src_head, "property", "og:type") or "website"
    og_img = meta(src_head, "property", "og:image")
    og_img = ASSET_RE.sub(asset_path, og_img).replace(DOMAIN, "")
    if not og_img or og_img.startswith("http"):  # fremde Platzhalter (z. B. Lovable-Vorschau) ersetzen
        og_img = "/img/neu_01_Schlafzimmer_1.jpg"
    og_img = DOMAIN + og_img

    over = SEO.get(path, {})
    title = over.get("title", title)
    desc = over.get("description", desc)
    canonical = DOMAIN + path

    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src_head, re.S)
    ld_out = []
    for block in ld:
        data = json.loads(block)
        data = json.loads(ASSET_RE.sub(asset_path, json.dumps(data, ensure_ascii=False)))
        fix_ld(data, og_img)
        ld_out.append(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    preload = ""
    if path == "/":
        preload = '<link rel="preload" as="image" href="/img/neu_01_Schlafzimmer_1.jpg" fetchpriority="high">\n'

    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="canonical" href="{canonical}">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<meta name="theme-color" content="#3b2f2a">',
        '<meta name="geo.region" content="DE-BY">',
        '<meta name="geo.placename" content="Bernau am Chiemsee">',
        '<meta name="geo.position" content="47.8117;12.3861">',
        '<meta name="ICBM" content="47.8117, 12.3861">',
        '<link rel="preload" href="/fonts/Brandon_light.otf" as="font" type="font/otf" crossorigin>',
        preload.strip(),
        '<link rel="stylesheet" href="/assets/styles.css">',
        '<link rel="stylesheet" href="/assets/site.css">',
        f'<meta property="og:locale" content="de_DE">',
        f'<meta property="og:site_name" content="Das Bergloft">',
        f'<meta property="og:title" content="{esc(og_title)}">',
        f'<meta property="og:description" content="{esc(og_desc)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{og_img}">' if og_img else "",
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(og_title)}">',
        f'<meta name="twitter:description" content="{esc(og_desc)}">',
        f'<meta name="twitter:image" content="{og_img}">' if og_img else "",
    ]
    parts += [f'<script type="application/ld+json">{b}</script>' for b in ld_out]
    return "\n".join(p for p in parts if p)


GALLERY_IMAGES = []


def fix_ld(data, og_img):
    """Strukturierte Daten vervollständigen (absolute URLs, Bilder, konsistente Texte)."""
    def absolutize(v):
        if isinstance(v, str) and v.startswith("/img/"):
            return DOMAIN + v
        return v

    if isinstance(data, dict):
        for k, v in list(data.items()):
            if isinstance(v, (dict, list)):
                fix_ld(v, og_img)
            else:
                data[k] = absolutize(v)
        if data.get("@type") == "LodgingBusiness":
            data["@id"] = DOMAIN + "/#bergloft"
            data["name"] = "Das Bergloft – Ferienwohnung Bernau am Chiemsee"
            data["alternateName"] = "Das Bergloft"
            data["image"] = [DOMAIN + "/img/" + n for n in GALLERY_IMAGES[:8]] or og_img
            data["email"] = "simone@alpenglueck-apartments.at"
            data["address"]["@type"] = "PostalAddress"
            data["address"]["addressLocality"] = "Bernau am Chiemsee"
            data["numberOfBedrooms"] = 2
            data["smokingAllowed"] = False
            data["amenityFeature"] += [
                {"@type": "LocationFeatureSpecification", "name": n, "value": True}
                for n in ["Kostenlose Einzelgarage", "Babybett und Hochstuhl", "Smart TV", "Geschirrspüler"]
            ]
        if data.get("@type") == "Answer" and "vor der Anreise per Link" in data.get("text", ""):
            # an den sichtbaren Seitentext angleichen
            data["text"] = data["text"].replace("vor der Anreise per Link", "am Abreisetag per Link")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, (dict, list)):
                fix_ld(v, og_img)
            else:
                data[i] = absolutize(v)


INQUIRY_FORM = """
<form id="anfrage-form" hidden novalidate class="mt-10 rounded-2xl bg-background/60 px-6 py-8 text-left shadow-soft sm:px-8">
<p class="text-eyebrow text-primary">Schnellanfrage</p>
<div class="mt-6 grid gap-5 sm:grid-cols-2">
<div><label for="name" class="text-sm font-medium">Name</label><input id="name" name="name" type="text" required autocomplete="name" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none" placeholder="Vor- und Nachname"></div>
<div><label for="email" class="text-sm font-medium">E-Mail</label><input id="email" name="email" type="email" required autocomplete="email" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none" placeholder="deine@email.de"></div>
<div><label for="arrival" class="text-sm font-medium">Anreise</label><input id="arrival" name="arrival" type="date" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none"></div>
<div><label for="departure" class="text-sm font-medium">Abreise</label><input id="departure" name="departure" type="date" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none"></div>
<div class="sm:col-span-2"><label for="guests" class="text-sm font-medium">Anzahl Gäste</label><select id="guests" name="guests" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none"><option value="">Bitte wählen</option><option value="1">1 Gast</option><option value="2">2 Gäste</option><option value="3">3 Gäste</option><option value="4">4 Gäste</option></select></div>
<div class="sm:col-span-2"><label for="message" class="text-sm font-medium">Nachricht <span class="font-normal text-muted-foreground">(optional)</span></label><textarea id="message" name="message" rows="4" class="mt-2 w-full rounded-xl border border-foreground/10 bg-background px-4 py-2.5 text-sm focus:border-primary focus:outline-none" placeholder="Fragen, Wünsche oder besondere Anlässe …"></textarea></div>
</div>
<div class="mt-8 flex flex-col flex-wrap gap-3 sm:flex-row">
<a data-send="whatsapp" href="https://wa.me/4368110613284" target="_blank" rel="noreferrer" class="rounded-full bg-gradient-sun px-7 py-3 text-center text-sm font-bold text-primary-foreground shadow-soft transition-transform hover:-translate-y-0.5">Per WhatsApp senden</a>
<a data-send="mail" href="mailto:simone@alpenglueck-apartments.at" class="rounded-full border border-foreground/20 px-7 py-3 text-center text-sm transition-colors hover:border-primary hover:text-primary">Per E-Mail senden</a>
<a data-send="gmail" href="https://mail.google.com/" target="_blank" rel="noreferrer" class="rounded-full border border-foreground/20 px-7 py-3 text-center text-sm transition-colors hover:border-primary hover:text-primary">Mit Gmail senden</a>
<a data-send="outlook" href="https://outlook.live.com/" target="_blank" rel="noreferrer" class="rounded-full border border-foreground/20 px-7 py-3 text-center text-sm transition-colors hover:border-primary hover:text-primary">Mit Outlook senden</a>
<button type="button" data-send="copy" class="rounded-full border border-foreground/20 px-7 py-3 text-sm transition-colors hover:border-primary hover:text-primary">Anfrage kopieren</button>
<button type="button" data-send="cancel" class="rounded-full border border-foreground/20 px-7 py-3 text-sm transition-colors hover:border-primary hover:text-primary">Abbrechen</button>
</div>
<p class="mt-4 text-xs text-muted-foreground">WhatsApp, Gmail oder Outlook öffnen sich direkt mit Deiner fertigen Anfrage. Alternativ kannst Du die vollständige Anfrage kopieren.</p>
</form>"""

LIGHTBOX = """
<div id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Bildansicht">
<button type="button" class="lb-btn lb-close" data-lb="close" aria-label="Schließen">×</button>
<button type="button" class="lb-btn lb-prev" data-lb="prev" aria-label="Vorheriges Bild">‹</button>
<figure><img alt=""><figcaption></figcaption></figure>
<button type="button" class="lb-btn lb-next" data-lb="next" aria-label="Nächstes Bild">›</button>
</div>"""

XENTRA_SCRIPT = ('<script async src="https://api.myxentra.com/functions/v1/widget-embed-js'
                 '?token=a268e3367d2b3e0611ceb7d0099cbc04"></script>')


def build_body(src, path):
    body = src[src.find("<body>") + len("<body>"):src.rfind("</body>")]
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)  # React/Lovable-Skripte raus
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = ASSET_RE.sub(asset_path, body)
    body = body.replace(" opacity-0 blur-[2px]", "")  # Bilder sofort sichtbar (ohne React-Fade)
    body = body.replace('fetchPriority=', 'fetchpriority=').replace('srcSet=', 'srcset=')

    if path == "/":
        # SEO: Hauptsuchbegriff in die H1 (optisch unverändert: gleiche Klassen)
        body = body.replace(
            '<p class="text-eyebrow text-accent text-shadow-hero">Bernau am Chiemsee · Chiemgau</p>'
            '<h1 class="mt-6 text-4xl leading-[1.08] tracking-tight text-secondary text-shadow-hero md:text-6xl">'
            'Alpenjuwel mit Bergblick<span class="block italic text-accent">am Bach.</span></h1>',
            '<h1 class="text-eyebrow text-accent text-shadow-hero">Ferienwohnung in Bernau am Chiemsee · Chiemgau</h1>'
            '<p class="mt-6 text-4xl leading-[1.08] tracking-tight text-secondary text-shadow-hero md:text-6xl">'
            'Alpenjuwel mit Bergblick<span class="block italic text-accent">am Bach.</span></p>', 1)
        assert "Ferienwohnung in Bernau am Chiemsee · Chiemgau</h1>" in body, "Hero nicht gefunden"
        # Anfrage-Button öffnet Formular
        body = body.replace('<button type="button" class="cursor-pointer rounded-full bg-gradient-sun',
                            '<button type="button" data-open-form class="cursor-pointer rounded-full bg-gradient-sun', 1)
        anchor = '<div class="mx-auto max-w-2xl text-center"><div class="mt-10 flex flex-wrap justify-center gap-4">'
        assert anchor in body, "Buchungsbereich nicht gefunden"
        body = body.replace(anchor, '<div class="mx-auto max-w-2xl text-center">' + INQUIRY_FORM +
                            '<div id="anfrage-buttons" class="mt-10 flex flex-wrap justify-center gap-4">', 1)
        # WhatsApp direkt neben "Anrufen"
        body = body.replace('>Anrufen</a>', '>Anrufen</a><a href="https://wa.me/4368110613284" target="_blank" '
                            'rel="noreferrer" class="rounded-full border border-foreground/20 px-7 py-3 text-sm '
                            'transition-colors hover:border-primary hover:text-primary">WhatsApp</a>', 1)
        body += LIGHTBOX + XENTRA_SCRIPT

    body = body.replace("Angaben gemäß § 5 TMG", "Angaben gemäß § 5 DDG")  # TMG seit 05/2024 abgelöst
    # Footer-Überschrift mit Suchbegriff ist schon vorhanden; Jahr statisch + per JS aktuell
    body += '<script src="/assets/site.js" defer></script>'
    return body


def relativize(page, depth):
    """Pfade relativ machen, damit die Seite auch unter einer Test-Adresse mit Unterordner funktioniert."""
    pre = "../" * depth
    page = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{pre}', page)
    page = re.sub(r'((?:srcset)="[^"]*")', lambda m: m.group(1).replace(" /img/", f" {pre}img/").replace('"/img/', f'"{pre}img/'), page)
    page = page.replace('href=""', 'href="./"').replace('href="#', 'href="#')
    page = page.replace(f'href="{pre}#', f'href="{pre or "./"}#') if pre else page.replace('href="#buchen"', 'href="#buchen"')
    return page


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    shutil.copytree(os.path.join(ROOT, "img_src"), os.path.join(OUT, "img"))
    shutil.copytree(os.path.join(ROOT, "fonts_src"), os.path.join(OUT, "fonts"))
    shutil.copy(os.path.join(RAW, "favicon.ico"), OUT)
    css = open(os.path.join(RAW, "styles.css"), encoding="utf-8").read()
    open(os.path.join(OUT, "assets", "styles.css"), "w", encoding="utf-8").write(ASSET_RE.sub(asset_path, css).replace("url(/fonts/", "url(../fonts/"))
    for f in ("site.js", "site.css"):
        shutil.copy(os.path.join(ROOT, "static", f), os.path.join(OUT, "assets", f))

    home = open(os.path.join(RAW, "index.html"), encoding="utf-8").read()
    GALLERY_IMAGES.extend(dict.fromkeys(
        re.findall(r"/__l5e/assets-v1/[0-9a-f-]{36}/(neu_[^\"/ ]+?\.jpg) 2000w", home)))

    for src_name, (out_name, path) in PAGES.items():
        src = open(os.path.join(RAW, src_name), encoding="utf-8").read()
        head = src[:src.find("</head>")]
        page = ('<!DOCTYPE html>\n<html lang="de">\n<head>\n' + build_head(head, path) +
                "\n</head>\n<body>" + build_body(src, path) + "\n</body>\n</html>\n")
        dest = os.path.join(OUT, out_name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        page = relativize(page, out_name.count("/"))
        open(dest, "w", encoding="utf-8").write(page)

    # 404-Seite aus dem Original
    src = open(os.path.join(RAW, "datenschutz.html"), encoding="utf-8").read()
    page = ('<!DOCTYPE html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>Seite nicht gefunden | Das Bergloft</title>\n<meta name="robots" content="noindex">\n'
            '<link rel="icon" href="/favicon.ico">\n<link rel="stylesheet" href="/assets/styles.css">\n'
            '</head>\n<body>' + build_body(src, "/404") + "\n</body>\n</html>\n")
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(page)

    # Sitemap
    urls = [p for _, p in PAGES.values() if p != "/impressum"]
    prio = {"/": "1.0", "/reisetipps": "0.8"}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in urls:
        sm.append(f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{TODAY}</lastmod>"
                  f"<priority>{prio.get(p, '0.7')}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")

    for f in ("robots.txt", "llms.txt", "_headers"):
        shutil.copy(os.path.join(ROOT, "static", f), OUT)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print("fertig:", OUT)


if __name__ == "__main__":
    main()
