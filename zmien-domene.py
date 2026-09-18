#!/usr/bin/env python3
"""Przełącza stronę z adresu GitHub Pages na własną domenę.

Uruchom DOPIERO wtedy, gdy domena jest kupiona, DNS ustawiony i GitHub Pages
pokazuje ją w ustawieniach repozytorium.

    python3 zmien-domene.py dominikabalcerzak.pl

Co robi:
  • podmienia adresy w canonical, hreflang i znacznikach Open Graph
    (index.html, polityka-prywatnosci.html, en/index.html, en/privacy-policy.html),
  • w 404.html zamienia ścieżki /dominika-balcerzak/... na /...,
  • tworzy plik CNAME dla GitHub Pages.

Potem zostaje: commit, push i sprawdzenie, czy https działa.
Cofnięcie: git checkout -- . (przed commitem).
"""
import pathlib
import re
import sys

STARY_ADRES = "https://pawelsypniewski.github.io/dominika-balcerzak/"
STARA_SCIEZKA = "/dominika-balcerzak/"

PLIKI = [
    "index.html",
    "polityka-prywatnosci.html",
    "en/index.html",
    "en/privacy-policy.html",
    "404.html",
]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    domena = sys.argv[1].strip().lower().removeprefix("https://").removeprefix("http://").rstrip("/")
    if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", domena):
        print(f"To nie wygląda na adres domeny: {domena}")
        return 1

    nowy_adres = f"https://{domena}/"
    katalog = pathlib.Path(__file__).parent

    for nazwa in PLIKI:
        plik = katalog / nazwa
        tekst = plik.read_text(encoding="utf-8")
        zmieniony = tekst.replace(STARY_ADRES, nowy_adres)
        # zdanie w polityce prywatności: „przyszedłeś z adresu pawelsypniewski.github.io”
        zmieniony = zmieniony.replace("pawelsypniewski.github.io", domena)
        if nazwa == "404.html":
            zmieniony = zmieniony.replace(STARA_SCIEZKA, "/")
        if zmieniony != tekst:
            plik.write_text(zmieniony, encoding="utf-8")
            print(f"{nazwa}: podmienione")
        else:
            print(f"{nazwa}: bez zmian (sprawdź ręcznie)")

    (katalog / "CNAME").write_text(domena + "\n", encoding="utf-8")
    print(f"CNAME: {domena}")

    zostalo = [
        f"{p.name}:{i}"
        for p in katalog.rglob("*.html")
        for i, w in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if "pawelsypniewski.github.io" in w
    ]
    print("Stary adres został jeszcze w:", ", ".join(zostalo) if zostalo else "nigdzie")

    print(
        "\nDalej:\n"
        "  1. git add -A && git commit -m 'Własna domena' && git push\n"
        "  2. GitHub → Settings → Pages → Custom domain → wpisz domenę, zaznacz „Enforce HTTPS”\n"
        "  3. Zaktualizuj politykę prywatności, jeśli zmienia się administrator danych lub hosting\n"
        "  4. Search Console: dodaj usługę dla nowego adresu i wyślij mapę strony"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
