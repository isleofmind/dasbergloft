# Das Bergloft – Website (ohne Lovable)

Statische Website für https://dasbergloft.de – kein Framework, keine Datenbank, keine laufenden Kosten.

## Ordner

| Ordner/Datei | Inhalt |
|---|---|
| `docs/` | **Die fertige Website.** GitHub Pages veröffentlicht genau diesen Ordner. |
| `build.py` | Erzeugt `docs/` neu aus `raw/`, `img_src/`, `fonts_src/`, `static/` (`python3 build.py`). |
| `raw/` | Sicherung der Original-Seiten von Lovable (Stand 21.11.2026). |
| `img_src/`, `fonts_src/` | Alle 97 Bilder und die 4 Schriftdateien. |
| `static/` | Galerie/Formular-Skript, Zusatz-CSS, robots.txt, llms.txt, Cache-Header. |

## Kostenlos hosten mit Cloudflare Pages (empfohlen)

1. Kostenloses Konto auf https://dash.cloudflare.com anlegen.
2. **Workers & Pages → Create → Pages → Upload assets** (Direkt-Upload) → Projektname `dasbergloft` → den Ordner `docs/` hochladen → Deploy.
   *(Alternativ: dieses Projekt in ein GitHub-Repository legen und Pages damit verbinden – dann geht jede Änderung automatisch live.)*
3. Testen unter `https://dasbergloft.pages.dev`.
4. **Custom domains → Set up a domain →** `dasbergloft.de` und `www.dasbergloft.de` hinzufügen und den DNS-Anweisungen folgen
   (beim Domain-Anbieter entweder die Nameserver auf Cloudflare umstellen oder einen CNAME-Eintrag setzen).
5. Erst wenn die neue Seite unter dasbergloft.de läuft: Domain in Lovable trennen und das Lovable-Abo kündigen.

> Wichtig: Wurde die Domain **über Lovable gekauft**, sie vor dem Kündigen zu einem eigenen Anbieter umziehen
> (z. B. Cloudflare Registrar, INWX, IONOS) – sonst kann die Domain verloren gehen.

## Nach dem Umzug (SEO)

- Google Search Console: Domain bestätigen, `https://dasbergloft.de/sitemap.xml` einreichen.
- Bing Webmaster Tools: Sitemap einreichen (Bing speist auch ChatGPT und andere KI-Suchen).
- Google Unternehmensprofil (Business Profile) für „Das Bergloft – Ferienwohnung Bernau am Chiemsee“ anlegen – das ist der
  stärkste Hebel für die lokale Suche „Ferienwohnung Bernau“ (Karte/Local Pack). Fotos hochladen, Gäste um Bewertungen bitten.
