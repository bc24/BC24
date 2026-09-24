"""Liest die neuesten Artikel von frank-panzer.de/blog und schreibt sie in die README."""
import re
import urllib.request
from html.parser import HTMLParser

BLOG_URL = "https://frank-panzer.de/blog/"
BASE_URL = "https://frank-panzer.de"
ANZAHL = 5
KATEGORIEN = {"web", "personal"}  # "angebot" wird ausgelassen
README = "README.md"
START, ENDE = "<!-- BLOG-START -->", "<!-- BLOG-ENDE -->"


class BlogParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.artikel, self.aktuell, self.in_h3 = [], None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "fp-blog-card" in (a.get("class") or ""):
            self.aktuell = {"href": a.get("href", ""), "datum": a.get("data-date", ""),
                            "kat": a.get("data-cat", ""), "titel": ""}
        elif tag == "h3" and self.aktuell is not None:
            self.in_h3 = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
        elif tag == "a" and self.aktuell is not None:
            self.artikel.append(self.aktuell)
            self.aktuell = None

    def handle_data(self, data):
        if self.in_h3 and self.aktuell is not None:
            self.aktuell["titel"] += data


def main():
    req = urllib.request.Request(BLOG_URL, headers={"User-Agent": "bc24-readme-bot"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    parser = BlogParser()
    parser.feed(html)

    artikel = [a for a in parser.artikel if a["titel"].strip() and a["kat"] in KATEGORIEN]
    artikel.sort(key=lambda a: a["datum"], reverse=True)
    if not artikel:
        raise SystemExit("Keine Artikel gefunden – README bleibt unverändert.")

    zeilen = []
    for a in artikel[:ANZAHL]:
        titel = " ".join(a["titel"].split()).replace("[", "(").replace("]", ")")
        url = a["href"] if a["href"].startswith("http") else BASE_URL + a["href"]
        j, m, t = (a["datum"].split("-") + ["", "", ""])[:3]
        datum = f"{t}.{m}.{j}" if t else ""
        zeilen.append(f"- [{titel}]({url})" + (f" · {datum}" if datum else ""))

    with open(README, encoding="utf-8") as f:
        inhalt = f.read()
    neu = re.sub(re.escape(START) + r".*?" + re.escape(ENDE),
                 START + "\n" + "\n".join(zeilen) + "\n" + ENDE, inhalt, flags=re.S)
    if neu != inhalt:
        with open(README, "w", encoding="utf-8") as f:
            f.write(neu)
        print("README aktualisiert.")
    else:
        print("Keine Änderung.")


if __name__ == "__main__":
    main()
