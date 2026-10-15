#!/usr/bin/env python3
"""Bouw publieke leespagina's, tekstbestanden, AI-ingangen en sitemap uit nl-opv."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://open-parafrase-weergave.nl"
NAME = "Open Parafrase Weergave"
GROUPS = {"OT": "Oude Testament", "NT": "Nieuwe Testament",
          "AP": "Apocriefe boeken", "ET": "Ethiopische boeken"}
IMAGE = "/images/psalm-23-herder.webp"
BOOK_ORDER = """genesis exodus leviticus numeri deuteronomium jozua richteren ruth
1samuel 2samuel 1koningen 2koningen 1kronieken 2kronieken ezra nehemia esther
job psalmen spreuken prediker hooglied jesaja jeremia klaagliederen ezechiel daniel
hosea joel amos obadja jona micha nahum habakuk zefanja haggai zacharia maleachi
mattheus markus lukas johannes handelingen romeinen 1korinthiers 2korinthiers
galaten efeziers filippenzen kolossenzen 1tessalonicensen 2tessalonicensen
1timotheus 2timotheus titus filemon hebreeen jakobus 1petrus 2petrus 1johannes
2johannes 3johannes judas openbaring
3ezra 4ezra tobit judith boekderwijsheid jezussirach baruch estherapocrief
gebedvanazaria gezangindevuuroven susanna belenddedraak gebedvanmanasse
1makkabeeen 2makkabeeen 3makkabeeen henoch jubileeen 1meqabyan 2meqabyan 3meqabyan 4baruch""".split()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(text)


def catalog(root: Path) -> list[dict]:
    manifest = json.loads((root / "data/vertalingen/manifest.json").read_text(encoding="utf-8"))
    published = set(next(e["boeken"] for e in manifest["edities"] if e["code"] == "nl-opv"))
    books = json.loads((root / "data/books.json").read_text(encoding="utf-8"))["books"]
    result = []
    for book in books:
        if book["id"] not in published:
            continue
        folder = root / "data/vertalingen/nl-opv" / book["id"]
        files = sorted((p for p in folder.glob("*.json") if p.stem.isdigit()), key=lambda p: int(p.stem))
        if not files:
            raise ValueError(f"Geen leeseditie voor {book['id']}")
        chapters = [json.loads(path.read_text(encoding="utf-8")) for path in files]
        if any(not chapter.get("verzen") for chapter in chapters):
            raise ValueError(f"Leeg hoofdstuk in {book['id']}")
        result.append({**book, "chapters": chapters})
    if len(result) != len(published):
        raise ValueError("Niet alle gepubliceerde boeken staan in de boekencatalogus")
    order = {book_id: index for index, book_id in enumerate(BOOK_ORDER)}
    return sorted(result, key=lambda book: (order.get(book["id"], len(order)), book["id"]))


def chapter_path(book: dict, chapter: dict) -> str:
    return f"/bijbel/{book['id']}/{chapter['hoofdstuk']}.html"


def schema_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def page(title: str, description: str, path: str, body: str, crumbs: list[tuple[str, str]],
         creative_work: dict | None = None, text_path: str | None = None,
         reader_path: str = "/index.html#johannes/1") -> str:
    graph = [{"@type": "WebPage", "@id": BASE + path, "url": BASE + path,
              "name": title, "description": description, "inLanguage": "nl-NL",
              "isPartOf": {"@id": BASE + "/#website"}},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": i, "name": name, "item": BASE + url}
                 for i, (name, url) in enumerate(crumbs, 1)]}]
    if creative_work:
        graph.append(creative_work)
    alternate = (f'<link rel="alternate" type="text/plain" href="{escape(text_path)}" title="Platte tekst">'
                 if text_path else "")
    breadcrumb = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="{escape(url)}">{escape(name)}</a>' for name, url in crumbs[:-1])
    breadcrumb += f' <span aria-hidden="true">/</span> <span aria-current="page">{escape(crumbs[-1][0])}</span>'
    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | {NAME}</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{BASE}{escape(path)}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="manifest" href="/manifest.json">
<link rel="alternate" type="text/plain" href="/llms.txt" title="Informatie voor AI en hergebruik">
{alternate}
<meta name="theme-color" content="#142e42">
<meta property="og:type" content="{'article' if creative_work else 'website'}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="nl_NL">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{BASE}{escape(path)}">
<meta property="og:image" content="{BASE}{IMAGE}">
<meta property="og:image:alt" content="Een herder met schapen bij stil water, illustratie bij Psalm 23">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title, quote=True)}">
<meta name="twitter:description" content="{escape(description, quote=True)}">
<meta name="twitter:image" content="{BASE}{IMAGE}">
<script type="application/ld+json">{schema_json({'@context': 'https://schema.org', '@graph': graph})}</script>
<script src="/js/theme.js"></script>
<script src="/js/sites.js" defer></script>
<link rel="stylesheet" href="/css/fonts.css">
<link rel="stylesheet" href="/css/style.css">
<link rel="stylesheet" href="/css/opv.css?v=1.0.2">
<link rel="stylesheet" href="/css/leespaginas.css?v=1.0.1">
</head>
<body class="opw-statisch">
<a class="opw-skip" href="#inhoud">Direct naar de inhoud</a>
<header class="opw-sitekop">
<a class="opv-merk" href="/"><img class="opv-carey" src="/images/branding/william-carey-missions.png" width="40" height="40" alt="William Carey"><span class="opv-merk-naam">{NAME}<small>de Bijbel, gewoon verteld</small></span></a>
<nav aria-label="Hoofdmenu"><a href="/bijbel/">Alle boeken</a><a href="{escape(reader_path)}">Lezer met instellingen</a><a href="/over-opv.html">Over OPW</a></nav>
</header>
<main class="opv-pagina" id="inhoud" tabindex="-1">
<nav class="opw-kruimels" aria-label="Broodkruimelpad">{breadcrumb}</nav>
{body}
</main>
<footer class="opv-voet"><span class="opv-ark">de kleine ark</span>
<nav aria-label="Meer informatie"><a href="/bijbel/">Alle Bijbelboeken</a><a href="/over-opv.html#status">Over de proeftekst</a><a href="/llms.txt">AI en hergebruik</a><a href="https://openvertaling.nl/" data-ov-href="">Open Vertaling</a><a href="https://opengodsword.com/wiki.html" data-ogw-href="wiki.html">Achtergrond</a></nav>
<span>Bijbeltekst: publiek domein · proefversie</span></footer>
</body>
</html>
'''


def sentence_lines(text: str) -> str:
    return re.sub(r'([.!?…][”’"\')\]]*)\s+(?=\S)', r'\1<br>', escape(text, quote=False))


def build_site(root: Path = ROOT) -> dict:
    books = catalog(root)
    sequence = [(book, chapter) for book in books for chapter in book["chapters"]]
    # De bron heeft geen publicatiedatum: checkouttijd is geen inhoudswijziging.
    # Daarom geen verzonnen lastmod-datums in de sitemap.
    urls = [("/", None), ("/over-opv.html", None), ("/bijbel/", None)]
    guide = f'''# {NAME} — de Bijbel in eenvoudig Nederlands

> Nederlandse parafrase van de Bijbel, naverteld vanuit de Statenvertaling 1888. Proefversie: alle verzen hebben de status concept. Uitgever: de kleine ark. De Bijbeltekst is publiek domein.

Er zijn {len(books)} boeken en {len(sequence)} hoofdstukken beschikbaar. De collectie omvat het Oude en Nieuwe Testament en daarnaast apocriefe en Ethiopische boeken. Die aanvullende boeken behoren niet in alle tradities tot de Bijbelcanon.

## Lezen en vinden
- [Alle Bijbelboeken]({BASE}/bijbel/): boekenoverzicht met links naar ieder hoofdstuk; volledig leesbaar zonder JavaScript.
- [Over de weergave]({BASE}/over-opv.html): doelgroep, bronbeleid, proefstatus en hergebruik.
- [Volledige tekst]({BASE}/llms-full.txt): alle beschikbare hoofdstukken als UTF-8-tekst; groot bestand.
- [Sitemap]({BASE}/sitemap.xml): canonieke HTML-adressen van boeken en hoofdstukken.

## Bronvermelding en gebruik
Noem de tekst "Open Parafrase Weergave (proef)". Vermeld boek, hoofdstuk en waar nodig vers. Dit is een parafrase en geen woordelijke vertaling uit de grondtekst. Presenteer de proeftekst niet als onafhankelijk door mensen goedgekeurd. De tekst is vrij te gebruiken, te kopiëren en te verspreiden.

Hoofdstukken staan op `/bijbel/BOEK/NUMMER.html`, met dezelfde tekst als platte tekst op `/bijbel/BOEK/NUMMER.txt`. Een specifiek vers heeft een anker `#vers-NUMMER`. De interactieve lezer staat op `/index.html#BOEK/NUMMER` en heeft leesinstellingen. Interne editiecode: `nl-opv`.

## Boeken en tekstbestanden
'''
    full = [f"# {NAME} (proef)\n\nBijbeltekst: publiek domein. Alle verzen: concept.\n"]
    for book in books:
        book_path = f"/bijbel/{book['id']}/"
        urls.append((book_path, None))
        title = book["nameDutch"]
        links = "".join(f'<li><a href="{chapter_path(book, chapter)}">Hoofdstuk {chapter["hoofdstuk"]}<span>{escape(chapter.get("kop", ""))}</span></a></li>' for chapter in book["chapters"])
        body = f'<h1>{escape(title)} in eenvoudig Nederlands</h1><p class="opv-lead">Lees {escape(title)} in de {NAME}. Kies een hoofdstuk om te beginnen.</p><p class="opv-pil">Proeftekst · alle verzen concept</p><ol class="opw-hoofdstukken">{links}</ol>'
        write(root / book_path.strip("/") / "index.html", page(
            f"{title} in eenvoudig Nederlands", f"Lees alle {len(book['chapters'])} hoofdstukken van {title} in de Open Parafrase Weergave. Gratis Bijbeltekst in eenvoudig Nederlands; proefversie.",
            book_path, body, [("Start", "/"), ("Bijbel", "/bijbel/"), (title, book_path)],
            reader_path=f"/index.html#{book['id']}/{book['chapters'][0]['hoofdstuk']}"))
        guide += f'- [{title}]({BASE}{book_path}): {len(book["chapters"])} hoofdstukken; [platte tekst]({BASE}{book_path}tekst.txt).\n'
        book_text = [f"# {title} — {NAME} (proef)\n\nBijbeltekst: publiek domein.\n"]
        for chapter in book["chapters"]:
            text = f"## {title} {chapter['hoofdstuk']} — {chapter.get('kop', '')}\n\n"
            text += "\n".join(f"{verse['nummer']}. {verse['tekst']}" for verse in chapter["verzen"]) + "\n"
            book_text.append(text)
            full.append(text)
            write(root / book_path.strip("/") / f"{chapter['hoofdstuk']}.txt", f"{NAME} (proef). Bijbeltekst: publiek domein.\n\n{text}")
        write(root / book_path.strip("/") / "tekst.txt", "\n".join(book_text))

    for index, (book, chapter) in enumerate(sequence):
        path = chapter_path(book, chapter)
        number = chapter["hoofdstuk"]
        ref = f"{book['nameDutch']} {number}"
        heading = chapter.get("kop") or ref
        description = f"{ref} in eenvoudig Nederlands. " + " ".join(chapter["verzen"][0]["tekst"].split())
        if len(description) > 170:
            description = description[:166].rsplit(" ", 1)[0] + "…"
        headings = {int(item["vers"]): item["tekst"] for item in chapter.get("blokken", []) if item.get("vers") and item.get("tekst")}
        verses = []
        for verse in chapter["verzen"]:
            if int(verse["nummer"]) in headings:
                verses.append(f'<h2>{escape(headings[int(verse["nummer"])])}</h2>')
            verses.append(f'<p id="vers-{int(verse["nummer"])}">{sentence_lines(verse["tekst"])}</p>')
        navigation = []
        for neighbor, relation, label in [(index - 1, "prev", "Vorige"), (index + 1, "next", "Volgende")]:
            if 0 <= neighbor < len(sequence):
                nb, nc = sequence[neighbor]
                navigation.append(f'<a href="{chapter_path(nb, nc)}" rel="{relation}">{label}: {escape(nb["nameDutch"])} {nc["hoofdstuk"]}</a>')
        subtitle = f'<p class="opw-hoofdstuktitel">{escape(heading)}</p>' if heading != ref else ''
        body = f'''<header class="opw-hoofdstukkop" aria-labelledby="hoofdstuk-titel">
<p class="opv-boven">{escape(GROUPS.get(book['testament'], 'Bijbel'))}</p>
<h1 id="hoofdstuk-titel">{escape(ref)}</h1>
{subtitle}
<p class="opv-pil">Proeftekst · alle verzen concept</p>
</header>
<p class="opw-leeshulp">Naverteld vanuit de Statenvertaling. <a href="/over-opv.html#status">Over deze proeftekst</a>.</p>
<div class="opw-bijbeltekst">{''.join(verses)}</div>
<nav class="opw-hoofdstuknav" aria-label="Hoofdstukken">{''.join(navigation)}</nav>
<div class="opv-acties"><a class="opv-knop" href="/index.html#{book['id']}/{number}">Lees met instellingen</a><a class="opv-knop opv-knop-zacht" href="{path.removesuffix('.html')}.txt">Platte tekst</a></div>'''
        work = {"@type": "Chapter", "@id": BASE + path + "#hoofdstuk", "name": f"{ref}: {heading}",
                "position": number, "inLanguage": "nl-NL", "isAccessibleForFree": True,
                "creativeWorkStatus": "Concept", "copyrightNotice": "Bijbeltekst: publiek domein",
                "isPartOf": {"@type": "Book", "name": f"{book['nameDutch']} — {NAME}",
                             "url": f"{BASE}/bijbel/{book['id']}/"}}
        write(root / path.lstrip("/"), page(f"{ref} — {heading}", description, path, body,
              [("Start", "/"), ("Bijbel", "/bijbel/"), (book["nameDutch"], f"/bijbel/{book['id']}/"), (ref, path)], work, path.removesuffix(".html") + ".txt",
              reader_path=f"/index.html#{book['id']}/{number}"))
        urls.append((path, None))

    sections = []
    for group, label in GROUPS.items():
        links = "".join(f'<li><a href="/bijbel/{book["id"]}/">{escape(book["nameDutch"])}<span>{len(book["chapters"])} hoofdstukken</span></a></li>' for book in books if book["testament"] == group)
        if links:
            sections.append(f'<section aria-labelledby="groep-{group}"><h2 id="groep-{group}">{label}</h2><ul class="opw-boeken">{links}</ul></section>')
    body = f'<h1>De Bijbel in eenvoudig Nederlands</h1><p class="opv-lead">Alle {len(books)} boeken en {len(sequence)} hoofdstukken van de {NAME}. Kies een boek en daarna een hoofdstuk.</p><p class="opv-pil">Proeftekst · alle verzen concept</p><p>De apocriefe en Ethiopische boeken staan apart; hun plaats in de Bijbelcanon verschilt per traditie.</p>{"".join(sections)}'
    write(root / "bijbel/index.html", page("Alle Bijbelboeken in eenvoudig Nederlands", f"Lees de Bijbel gratis in eenvoudig Nederlands: {len(books)} boeken en {len(sequence)} hoofdstukken. Open Parafrase Weergave, proefversie.", "/bijbel/", body, [("Start", "/"), ("Bijbel", "/bijbel/")]))
    guide += f'''\n## Verwante bronnen
- [Open Vertaling](https://openvertaling.nl/): herziene Statenvertaling voor wie een meer woordelijke weergave wil lezen.
- [Open Gods Woord](https://opengodsword.com/wiki.html): Bijbelachtergrond en broninformatie.
'''
    write(root / "llms.txt", guide)
    write(root / "LLM.txt", guide)
    write(root / "llms-full.txt", "\n".join(full))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, date in urls:
        modified = f"<lastmod>{date}</lastmod>" if date else ""
        sitemap.append(f"  <url><loc>{xml_escape(BASE + path)}</loc>{modified}</url>")
    write(root / "sitemap.xml", "\n".join(sitemap) + "\n</urlset>\n")
    return {"boeken": len(books), "hoofdstukken": len(sequence)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(build_site(parser.parse_args().root), ensure_ascii=False))
